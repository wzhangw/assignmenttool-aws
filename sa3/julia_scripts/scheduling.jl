#importing useful packages
using CSV, JuMP, Cbc, DataFrames, DelimitedFiles

Input = ARGS;
global folder = "media/"
global userid = string(Input[1])
global username = Input[2]
global id = string(Input[3])


student_dict=Dict()
all_events=[]
# import faculty meeting data if available
try
    global B= readdlm(folder*userid*"_"*username*"/model_"*id*"/Faculty_time.csv",',')
    global num_faculty=length(B[1,2:end])
    global faculty=B[1, 2:2+num_faculty-1]
    global A= readdlm(folder*userid*"_"*username*"/model_"*id*"/Student_pref.csv",',')
    global num_student_1=length(A[1,2:end])
    global student_1=A[1, 2:2+num_student_1-1]
    global time_1=convert(Array, B[:,1]);
    global n=7;
    global p=20;
    global len_fac=1
    global all_events=union(all_events,B[1,2:end])
    for i in 1:num_student_1
        global student_dict[student_1[i]]=Dict()
        for j in 1:num_faculty
            if A[j+1,i+1] == ""
                student_dict[student_1[i]][faculty[j]]=0
            else
                student_dict[student_1[i]][faculty[j]]=A[j+1,i+1]
            end
        end
    end
    global faculty_dict=Dict()
    for j in 1:num_faculty
        faculty_dict[faculty[j]]=Dict()
        for k in 2:length(time_1)
            faculty_dict[faculty[j]][time_1[k]]=B[k,j+1]
        end
    end
    println("Faculty meeting data imported.")
catch ArgumentError
    println(ArgumentError)
    println("No individual meetings")
    global num_faculty=0
    global student_names_1=nothing
    global time_1=nothing
end

#import talk data if available
try
    global C=readdlm(folder*userid*"_"*username*"/model_"*id*"/Talk_time.csv",',')
    global num_talks=length(C[1,2:end])
    global talks=C[1,2:2+num_talks-1]
    global D=readdlm(folder*userid*"_"*username*"/model_"*id*"/Talk_pref.csv",',')

    global num_student_2=length(D[1,2:end])
    global student_2=D[1,2:2+num_student_2-1]
    global time_2=convert(Array, C[:,1]);
    global m=1
    global len_talk=2
    global all_events=union(all_events,C[1,2:end])
    for i in 1:num_student_2
        for j in 1:num_talks
            if D[j+1,i+1] == ""
                student_dict[student_2[i]][talks[j]]=0
            else
                student_dict[student_2[i]][talks[j]]=D[j+1,i+1]
            end
        end
    end
    global talk_dict=Dict()
    for j in 1:num_talks
        talk_dict[talks[j]]=Dict()
        for k in 2:length(time_2)
            talk_dict[talks[j]][time_2[k]]=C[k,j+1]
        end
    end
    println("Talks data imported.")
catch ArgumentError
    println("No talks")
    global num_talks=0
    global student_2=nothing
    global time_2=nothing
end

#check if student info is consistent in both events
if (student_1 != nothing) & (student_2 != nothing) & (student_1 != student_2)
    print("students are not consistant in the data, please check the students input.")
else
    if student_1 != nothing
        student=student_1
        num_student=num_student_1
    else
        student=student_2
        num_student=num_student_2
    end
    println("student info consistent")
end

#import general event data if available
try
    global F=readdlm(folder*userid*"_"*username*"/model_"*id*"/Gen_time.csv",',')
    global num_gen_event=length(F[1,2:end])
    global general_event = F[1, 2:2+num_gen_event-1]
    global time_3 = convert(Array, F[:,1]);
    println("General event data imported.")
    global len_gen=1
    all_events=union(all_events, F[1, 2:end])
    for i in 1:num_student
        for j in 1:num_gen_event
            student_dict[student[i]][general_event[j]]=1
        end
    end
    global gen_event_dict=Dict()
    for j in 1:num_gen_event
        gen_event_dict[general_event[j]]=Dict()
        for k in 2:length(time_3)
            gen_event_dict[general_event[j]][time_3[k]]=F[k,j+1]
        end
    end
catch ArgumentError
    println("No general events")
    global num_gen_event=0
    global time_3=nothing
end

#check if time period info is consistent
if (time_1 != nothing) & (time_2 != nothing) & (time_1 != time_2)
    println("time periods not consistent")
elseif (time_1 != nothing) & (time_3 != nothing) & (time_1 != time_3)
    println("time periods not consistent")
elseif (time_2 != nothing) & (time_3 != nothing) & (time_2 != time_3)
    println("time periods not consistent")
else
    if time_1 != nothing
        period=time_1[2:end]
    elseif time_2 != nothing
        period=time_2[2:end]
    elseif time_3 != nothing
        period=time_3[2:end]
    end
    println("time periods info consistent")
end

#import the # of people limitation for each event
event_limit=Dict()
E = readdlm(folder*userid*"_"*username*"/model_"*id*"/num_limit.csv",',')
for j in 1:length(all_events)
    event_limit[all_events[j]]=Dict()
    event_limit[all_events[j]]["l"]=E[2,j+1]
    event_limit[all_events[j]]["u"]=E[3,j+1]
end

if length(student_dict)>0
    println("Data import complete. Ready to proceed.")
end

mm=Model(with_optimizer(Cbc.Optimizer))

@variable(mm, x[student, all_events, period], Bin)
@variable(mm, obj_fac)
@variable(mm, obj_talk)
@variable(mm, obj_gen)

if num_faculty > 0
    if len_fac > 1
        #they have to attend entire talk
        for j in faculty
            for k in 1:length(period)
                if faculty_dict[j][period[k]]==1
                    for z in 1:len_fac-1
                        @constraint(mm, [i in student], x[i,j,period[k]]==x[i,j,period[k+z]])
                    end
                    break
                end
            end
        end
    end
    #a student meets at least n faculties
    @constraint(mm, [i in student], sum(x[i,j,k] for j in faculty for k in period)>=n)
    #each faculty meets at most p students in total
    @constraint(mm, [j in faculty], sum(x[i,j,k] for i in student for k in period)<=p)
    #events are not available at some time slots
    @constraint(mm, [i in student, j in faculty, k in period], x[i,j,k]<=faculty_dict[j][k])
    #each student talk to a faculty just once
    @constraint(mm, [i in student, j in faculty], sum(x[i,j,k] for k in period)<=len_fac)
    @constraint(mm, obj_fac==sum(x[i,j,k]*student_dict[i][j] for i in student for j in faculty for k in period))
else
    @constraint(mm, obj_fac==0)
end

if num_talks > 0
    if len_talk > 1
        #they have to attend entire talk
        for j in talks
            for k in 1:length(period)
                if talk_dict[j][period[k]]==1
                    for z in 1:len_talk-1
                        @constraint(mm, [i in student], x[i,j,period[k]]==x[i,j,period[k+z]])
                    end
                    break
                end
            end
        end
    end
    #a students attends at least m talks
    @constraint(mm, [i in student], sum(x[i,j,k] for j in talks for k in period)>=m*len_talk)
    #events are not available at some time slots
    @constraint(mm, [i in student, j in talks, k in period], x[i,j,k]<=talk_dict[j][k])
    #each student attend talk for the full session and only once
    @constraint(mm, [i in student, j in talks], sum(x[i,j,k] for k in period)<=len_talk)
    @constraint(mm, obj_talk==sum(x[i,j,k]*student_dict[i][j] for i in student for j in talks for k in period)/len_talk)
else
    @constraint(mm, obj_talk==0)
end
if num_gen_event>0
    if len_gen > 1
        for j in general_event
            for k in 1:length(period)
                if gen_event_dict[j][period[k]]==1
                    for z in 1:len_talk-1
                        @constraint(mm, [i in student], x[i,j,period[k]]==x[i,j,period[k+z]])
                    end
                    break
                end
            end
        end
    end
    #a students must attend all general event once
    @constraint(mm, [i in student, j in general_event], sum(x[i,j,k] for k in period)==1)
    #events are not available at some time slots
    @constraint(mm, [i in student, j in general_event, k in period], x[i,j,k]<=gen_event_dict[j][k])
    #each student attend gen_event once for the full session
    @constraint(mm, [i in student, j in faculty], sum(x[i,j,k] for k in period)<=len_gen)
    @constraint(mm, obj_gen==sum(x[i,j,k]*student_dict[i][j] for i in student for j in general_event for k in period)/len_gen)
else
    @constraint(mm, obj_gen==0)
end
#for all events
#each student attend one event at one time slot
@constraint(mm, [i in student, k in period], sum(x[i,j,k] for j in all_events)<=1)
#event can take num_limit number of students
@constraint(mm, [j in all_events, k in period], sum(x[i,j,k] for i in student)<=event_limit[j]["u"])
@constraint(mm, [j in all_events, k in period], sum(x[i,j,k] for i in student)>=event_limit[j]["l"])

@objective(mm, Max, obj_fac+obj_talk+obj_gen)
status=optimize!(mm)


all_events_col=union([:time],all_events)
row=union(period,["total"])
R=DataFrame([String for i in 1:length(all_events_col)], Symbol.(all_events_col), length(row))
for i in 1:length(row)
    for j in 1:length(all_events_col)
        if j==1
            R[i,j]=row[i]
        else
            R[i,j]="-"
        end
    end
end

for i in 1:length(student)
    for j in 1:length(all_events)
        for k in 1:length(period)
            if value.(x[student[i],all_events[j],period[k]])==1
                if R[k,j+1]=="-"
                    R[k,j+1]=string(student[i])
                else
                    R[k,j+1]=string(R[k,j+1]," + ",string(student[i]))
                end
            end
        end
    end
end

if num_faculty != 0
    for j in 1:length(faculty)
        R[end,j+1]=string(sum(value.(x[i,faculty[j],k]) for i in student for k in period)/len_fac)
    end
end
if num_talks != 0
    for j in 1:length(talks)
                        R[end,j+num_faculty+1]=string(sum(value.(x[i,talks[j],k]) for i in student for k in period)/len_talk)
    end
end
if num_gen_event != 0
    for j in 1:length(general_event)
        R[end,j+num_faculty+num_talks+1]=string(sum(value.(x[i,general_event[j],k]) for i in student for k in period)/len_gen)
    end
end

for j in 1:length(all_events)
    R[end,j+1]=string(sum(value.(x[i,all_events[j],k]) for i in student for k in period))
end
CSV.write(folder*userid*"_"*username*"/model_"*id*"/results_pro_"*id*".csv", R)

col=union([:time],student)
row=union(period,["total"])
R=DataFrame([String for i in 1:length(col)],Symbol.(col), length(row))
for i in 1:length(row)
    for j in 1:length(col)
        if j==1
            R[i,j]=row[i]
        else
            R[i,j]="-"
        end
    end
end

for i in 1:length(student)
    for j in 1:length(all_events)
        for k in 1:length(period)
            if value.(x[student[i],all_events[j],period[k]])==1
                if R[k,i+1]=="-"
                    R[k,i+1]=string(all_events[j])
                else
                    R[k,i+1]=string(R[k,i+1]," + ",string(all_events[j]))
                end
            end
        end
    end
end

count=zeros(length(student))
if num_faculty != 0
    for i in 1:length(student)
        if len_fac>1
            count[i]+=sum(value.(x[student[i],j,k]) for j in faculty for k in period)-sum(value.(x[student[i],j,k]) for j in faculty for k in period)/len_fac
        else
            count[i]+=sum(value.(x[student[i],j,k]) for j in faculty for k in period)
        end
    end
end
if num_talks != 0
    for i in 1:length(student)
        if len_talk>1
            count[i]+=sum(value.(x[student[i],j,k]) for j in talks for k in period)-sum(value.(x[student[i],j,k]) for j in talks for k in period)/len_talk
        else
            count[i]+=sum(value.(x[student[i],j,k]) for j in talks for k in period)
        end
    end
end
if num_gen_event != 0
    for i in 1:length(student)
        if len_gen>1
            count[i]+=sum(value.(x[student[i],j,k]) for j in general_event for k in period)-sum(value.(x[student[i],j,k]) for j in general_event for k in period)/len_gen
        else
            count[i]+=sum(value.(x[student[i],j,k]) for j in general_event for k in period)
        end
    end
end

for i in 1:length(student)
    R[end,i+1]=string(count[i])
end
CSV.write(folder*userid*"_"*username*"/model_"*id*"/results_stu_"*id*".csv", R)

