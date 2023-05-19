#importing useful packages
using CSV, JuMP, Cbc, DataFrames, Dates

Input = ARGS;
folder = "media/"
userid = string(Input[1])
username = Input[2]
id = string(Input[3])
p_input = parse(Int64, Input[4])
n_input = parse(Int64, Input[5])
n_opt_input = parse(Int64, Input[6])

#input data
A=CSV.read(folder*userid*"_"*username*"/model_"*id*"/Student_pref.csv"); #input
B=CSV.read(folder*userid*"_"*username*"/model_"*id*"/Faculty_time.csv"); #input
E=CSV.read(folder*userid*"_"*username*"/model_"*id*"/num_limit.csv"); #input
p=p_input;#input, maximum number of student each faculty/meeting/lab should take in total, if don't care, put 10000
n=n_input; #input, least number of faculty a student should meet, set as 0 if not specified, if don't care, put 0
n_opt=n_opt_input;#input, optimal number of faculty a student should meet

#transform data to dictionary
student_dict=Dict()
num_faculty=length(B[1,2:end])
faculty=names(B)[2:2+num_faculty-1]
num_student=length(A[1,2:end])
student=names(A)[2:2+num_student-1]
time=convert(Array, B[:,1]);
max_pref=0
min_pref=Inf

#creating student preference dictionary
for i in 1:num_student
    student_dict[student[i]]=Dict()
    for j in 1:num_faculty
        if (ismissing(A[j,i+1])) | (A[j,i+1]==0)
            student_dict[student[i]][faculty[j]]=0
        else
            student_dict[student[i]][faculty[j]]=A[j,i+1]
        end
        if student_dict[student[i]][faculty[j]] > max_pref
            global max_pref=student_dict[student[i]][faculty[j]]
        end
        if student_dict[student[i]][faculty[j]] < min_pref
            global min_pref=student_dict[student[i]][faculty[j]]
        end
    end
end
for i in student
    for j in faculty
        if student_dict[i][j]!=0
            student_dict[i][j]=max_pref+1-student_dict[i][j]
        end
    end
end

#creating event timetable dictionary
faculty_dict=Dict()
for j in 1:num_faculty
    faculty_dict[faculty[j]]=Dict()
    for k in 1:length(time)
        if ismissing(B[k,j+1])
            faculty_dict[faculty[j]][time[k]]=0
        else
            faculty_dict[faculty[j]][time[k]]=B[k,j+1]
        end
    end
end

# creating dictionary of # of students limitation for each event
event_limit=Dict()
duration=Dict()
num_faculty_1=length(E[1,2:end])
faculty_1 = names(E)[2:2+num_faculty-1]
for j in 1:length(faculty_1)
    event_limit[faculty_1[j]]=Dict()
    event_limit[faculty_1[j]]["l"]=E[1,j+1]
    event_limit[faculty_1[j]]["u"]=E[2,j+1]
    duration[faculty_1[j]]=E[3,j+1]
end
println("Faculty meeting data imported.")

#Cross profile consistency check
error=0
if length(faculty)!=length(faculty_1)
    print("Faculty/Meeting/Event data inconsistent from Faculty_pref.csv and num_limit_csv")
    error+=1
else
    for i in faculty
        if ~(i in faculty_1)
            print("Faculty/Meeting/Event data inconsistent from Faculty_pref.csv and num_limit_csv")
            global error+=1
            break
        end
    end
end
if error==0
    println("Data consistency check passed.")
else
    println("Recheck data consistency between profiles Faculty_pref.csv and num_limit_csv.")
end

#Data type check
count=0
error=0
#check if time periods is an array of either stings or Dates.Time
if ~((time isa Array{Dates.Time}) | (time isa Array{String}))
    println("Time periods data type error, must be String or Dates.Time")
    error+=1
end
#check if student preference data is only number
for i in student
    for j in faculty
        if ~(student_dict[i][j] isa Number)
            global count+=1
        end
    end
end
if count != 0
    println("Student_pref.csv data type error, must be a number indicating their preference")
    count=0
    error+=1
end
#check if faculty time table is only number
for j in faculty
    for k in time
        if ~(faculty_dict[j][k] isa Number)
            global count+=1
        end
    end
end
if count != 0
    println("Faculty_time.csv data type error, must be a number")
    count=0
    error+=1
end
#check if faculty timetable is only 0 or 1
for j in faculty
    for k in time
        if (faculty_dict[j][k]!= 0) & (faculty_dict[j][k]!= 1)
            global count+=1
        end
    end
end
if count != 0
    println("Faculty_time.csv must contain only 0 or 1, other number found")
    error+=1
    count=0
end
#check if upper and lower bounds are all numbers and lower bound is smaller than upper bound
for j in faculty
    for l in ["u","l"]
        if ~(event_limit[j][l] isa Number)
            global count+=1
        end
    end
end
if count != 0
    println("num_limit.csv must contain only numbers")
    error+=1
    count=0
end
for j in faculty
    if event_limit[j]["u"] < event_limit[j]["l"]
        global count+=1
    end
end
if count != 0
    println("Upper limit must be larger than lower limit in num_limit.csv")
    error+=1
    count=0
end
#check if duration data are all numbers
for j in faculty
    if ~(duration[j] isa Number)
        global count+=1
    end
end
if count != 0
    println("Duration data in num_limit.csv must be numbers")
    error+=1
    count=0
end

#Summary
if error==0
    println("Data type check passed.")
else
    println("Recheck data type error.")
end

#Data dimension check
println("Summary of data and requirements:")
println("Total number of students is ", length(student))
println("Maximum student preference is ", max_pref, ". Minimum student preference is ", min_pref)
println("Total number of faculties/meetings/events is ", length(faculty))
println("Minimum number of meetings/events that a student should attend is ", n)
println("Total number of time periods is ", length(time))
println("If the preceding data summary is correct, please proceed")

M=100
#import Gurobi
mm=Model(with_optimizer(Cbc.Optimizer))

@variable(mm, x[student, faculty, time], Bin)
@variable(mm, obj_fac)
@variable(mm, y[student, faculty, time], Bin)
@variable(mm, z[student, faculty], Bin)

#each faculty meets at most p students in total
@constraint(mm, [j in faculty], sum(z[i,j] for i in student) <= p)
@constraint(mm, [i in student, j in faculty], z[i,j]<=sum(x[i,j,k] for k in time))
@constraint(mm, [i in student, j in faculty, k in 1:length(time)-duration[j]+1], sum(x[i,j,time[h]] for h in k:k+duration[j]-1)==y[i,j,time[k]]*sum(faculty_dict[j][time[h]] for h in k:k+duration[j]-1))

#events are not available at some time slots
@constraint(mm, [i in student, j in faculty, k in time], x[i,j,k]<=faculty_dict[j][k])
#each student talk to a faculty just once
@constraint(mm, [i in student, j in faculty], sum(x[i,j,k] for k in time)<=duration[j])


#student shold not attend any event that they are not interested
@constraint(mm, [i in student, j in faculty, k in time], x[i,j,k] <=student_dict[i][j])
#for all events
#each student attend one event at one time slot
@constraint(mm, [i in student, k in time], sum(x[i,j,k] for j in faculty)<=1)
#event can take num_limit number of students
@constraint(mm, [j in faculty, k in time], sum(x[i,j,k] for i in student)<=event_limit[j]["u"])
@constraint(mm, [j in faculty, k in time], sum(x[i,j,k] for i in student)>=event_limit[j]["l"])
#every student meet at least n faculty while maximize the number of students that meets n_max faculty
@constraint(mm, [i in student], sum(z[i,j] for j in faculty) >= n)
@variable(mm, slack[student], Bin)
@constraint(mm, [i in student], sum(x[i,j,k] for j in faculty for k in time)-n_opt+1<=M*slack[i])
@constraint(mm, [i in student], sum(x[i,j,k] for j in faculty for k in time)-n_opt>=-M*(1-slack[i]))
@constraint(mm, obj_fac==5*sum(slack)+sum(z[i,j]*student_dict[i][j] for i in student for j in faculty))
@objective(mm, Max, obj_fac)
optimize!(mm)

model_status = termination_status(mm)
open(folder*userid*"_"*username*"/model_"*id*"/model_status.csv", "w") do pr
    println(pr,"Solving time",",", "$(Dates.year(now()))-$(Dates.month(now()))-$(Dates.day(now())) $(Dates.hour(now())):$(Dates.minute(now()))");
    println(pr,"Model Status",",",string(model_status))
    println(pr,"Model Status Code",",",Int(model_status))
end


import Dates
periods=[]
for i in time
    if isa(i,Dates.Time)
        push!(periods,Dates.format(i,"HH:MM:SS"))
    else
        push!(periods,i)
    end

end
faculty_col=union([:time],faculty)
row=union(periods,["total"])
R=DataFrame([String for i in 1:length(faculty_col)], Symbol.(faculty_col), length(row))
for i in 1:length(row)
    for j in 1:length(faculty_col)
        if j==1
            R[i,j]=row[i]
        else
            R[i,j]="/"
        end
    end
end

for i in 1:length(student)
    for j in 1:length(faculty)
        for k in 1:length(time)
            if value.(x[student[i],faculty[j],time[k]])>=0.9
                if R[k,j+1]=="/"
                    R[k,j+1]=string(student[i])
                else
                    R[k,j+1]=string(R[k,j+1]," + ",string(student[i]))
                end
            end
        end
    end
end
for j in 1:length(faculty)
    R[end,j+1]=string(sum(value.(z[i,faculty[j]]) for i in student))
end

CSV.write(folder*userid*"_"*username*"/model_"*id*"/results_pro.csv", R)

col=union([:time],student)
row=union(periods,["total"])
R=DataFrame([String for i in 1:length(col)],Symbol.(col), length(row))
for i in 1:length(row)
    for j in 1:length(col)
        if j==1
            R[i,j]=row[i]
        else
            R[i,j]="/"
        end
    end
end

for i in 1:length(student)
    for j in 1:length(faculty)
        for k in 1:length(time)
            if value.(x[student[i],faculty[j],time[k]])>=0.9
                if R[k,i+1]=="/"
                    R[k,i+1]=string(faculty[j])
                else
                    R[k,i+1]=string(R[k,i+1]," + ",string(faculty[j]))
                end
            end
        end
    end
end

count=zeros(length(student))
for i in 1:length(student)
    count[i]+=sum(value.(z[student[i],j]) for j in faculty)
end

for i in 1:length(student)
    R[end,i+1]=string(count[i])
end
CSV.write(folder*userid*"_"*username*"/model_"*id*"/results_stu.csv", R)
