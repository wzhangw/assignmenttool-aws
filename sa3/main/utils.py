"""Select code path based on model type"""
def codeselector(modeltype):        # need to be consistent with TaskCreationForm
    if int(modeltype) == 1:         #
        return "julia_scripts/scheduling.jl"
    elif int(modeltype) == 2:       #
        return "julia_scripts/scheduling_room.jl"
    elif int(modeltype) == 3:
        return "julia_scripts/grad_assign.jl"

"""Data Checkers"""
def facultytimeDataChecker(facultytimedata, task):
    msg = []
    temp = facultytimedata[0][1:]
    Faculties = [item.replace(","," ") for item in temp]

    temp = [facultytimedata[i][0] for i in range(1, len(facultytimedata))]
    Periods = [item.replace(","," ") for item in temp]

    FacultyTime = [facultytimedata[i][j] for i in range(1, len(facultytimedata)) for j in range(1, len(facultytimedata[0]))]
    for item in FacultyTime:
        try:
            a = int(item)
            if a != 0 and a != 1:
                print(item)
                msg.append("Data should include 0 and 1 only!")
                msg = list(set(msg))
        except Exception as e:
            print(e)
            msg.append("Data should include 0 and 1 only!")
            msg = list(set(msg))

    if len(msg) == 0:
        temp = facultytimedata[0][1:]
        temp = [item.replace(","," ") for item in temp]
        task.Faculties = temp

        temp = [facultytimedata[i][0] for i in range(1, len(facultytimedata))]
        temp = [item.replace(","," ") for item in temp]
        task.Periods = temp

        task.FacultyTime = [facultytimedata[i][j] for i in range(1, len(facultytimedata)) for j in range(1, len(facultytimedata[0]))]

        if '2' not in task.finished_steps:
            task.finished_steps += '2'
        task.save()

    return msg


def studentprefDataChecker(studentprefdata, task):
    msg = []

    temp = studentprefdata[0][1:]
    Students = [item.replace(","," ") for item in temp]
    Faculties = [studentprefdata[i][0] for i in range(1, len(studentprefdata))]

    StudentsPref = [str(studentprefdata[i][j])*(studentprefdata[i][j]!='') + '0'*(studentprefdata[i][j]=='') for i in range(1, len(studentprefdata)) for j in range(1, len(studentprefdata[0]))]

    if list(Faculties) != list(task.Faculties):
        msg.append("Faculty data do not match with previous step!")
        msg = list(set(msg))

    for item in StudentsPref:
        try:
            a = int(item)
        except Exception as e:
            print(e)
            msg.append("Data should include integers only!")
            msg = list(set(msg))

    if len(msg) == 0:
        temp = studentprefdata[0][1:]
        temp = [item.replace(","," ") for item in temp]
        task.Students = temp

        temp = [str(studentprefdata[i][j])*(studentprefdata[i][j]!='') + '0'*(studentprefdata[i][j]=='') for i in range(1, len(studentprefdata)) for j in range(1, len(studentprefdata[0]))]
        task.StudentsPref = temp

        if '3' not in task.finished_steps:
            task.finished_steps += '3'
        task.save()

    return msg

def capacitydataDataChecker(capacitydata, task):
    msg = []

    faculties = capacitydata[0][1:]
    lowerlim = capacitydata[1][1:]
    upperlim = capacitydata[2][1:]
    duration = capacitydata[3][1:]

    if list(faculties) != list(task.Faculties):
        msg.append("Faculty data do not match with previous step!")
        msg = list(set(msg))

    for i in range(len(lowerlim)):
        l = lowerlim[i]
        u = upperlim[i]
        d = duration[i]

        try:
            l = int(l)
            u = int(u)
            d = int(d)
        except:
            msg.append("Capacity data should include integers only!")
            msg = list(set(msg))
        else:
            if l < 0 or u < 0 or d < 0:
                msg.append("Capacity should include positive numbers only!")
                msg = list(set(msg))
            elif u < l:
                msg.append("Upper limit should be larger or equal to lower limit!")
                msg = list(set(msg))
            else:
                pass

    if len(msg) == 0:
        faculties = capacitydata[0][1:]
        lowerlim = capacitydata[1][1:]
        upperlim = capacitydata[2][1:]
        duration = capacitydata[3][1:]

        task.LowerLimit = lowerlim
        task.UpperLimit = upperlim
        task.Duration = duration

        if '4' not in task.finished_steps:
            task.finished_steps += '4'
        task.save()

    return msg

def otherDataChecker(p, n, t, task):
    msg = []

    try:
        p = int(p)
        n = int(n)
        t = int(t)
    except:
        msg.append("Data should include integers only!")
        msg = list(set(msg))
    else:
        if p < 0 or n < 0 or t < 0:
            msg.append("Capacity should include positive numbers only!")
            msg = list(set(msg))

    if len(msg) == 0:
        task.p_val = p
        task.n_val = n
        task.t_val = t

        if '5' not in task.finished_steps:
            task.finished_steps += '5'
        task.save()

    return msg
