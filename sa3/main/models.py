from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django_mysql.models import ListTextField
import os
import csv
import shutil

def filepath(instance, filename):
    return '{0}_{1}/data_documents/{2}-{3}-{4}/{5}'.format(instance.user.id, instance.user.username, timezone.now().year, timezone.now().month, timezone.now().day, filename)

#def temppath(instance, filename):
#    return '{0}_{1}/temp_documents/{2}'.format(instance.user.id, instance.user.username, filename)
class DataDocumentNew(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    docfile = models.FileField(upload_to=filepath)
    date_upload = models.DateTimeField('date uploaded')

    def __str__(self):
        return str(self.docfile)

    def shortfilename(self):
        return os.path.basename(self.docfile.name)

    def delete(self, *args, **kwargs):
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.docfile.name))
        except:
            pass
        super(DataDocumentNew,self).delete(*args,**kwargs)

    def getcontent(self):
        with open(settings.MEDIA_ROOT + str(self.docfile), newline='') as csvfile:
            data = list(csv.reader(csvfile))
        return data



class DataDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    TYPES  =  [
        ('Faculty Time', 'Faculty Time'),
        ('Activity Capacity', 'Activity Capacity'),
        ('Faculty Room', 'Faculty Room'),
        ('Student Preference', 'Student Preference'),
        ('Talk Time', 'Talk Time'),
        ('Talk Preference', 'Talk Preference'),
        ('Event Time', 'Events Time'),
        ('Event Preference', 'Events Preference'),
        ('Room Time', 'Room Time'),
        ('Room Capacity', 'Room Capacity'),
    ]
    datatype = models.CharField(
        max_length=100,
        choices=TYPES ,
    )

    docfile = models.FileField(upload_to=filepath)
    date_upload = models.DateTimeField('date uploaded')
    notes = models.CharField(max_length = 200, default = 'No Notes')

    def __str__(self):
        return str(self.docfile)

    def shortfilename(self):
        return os.path.basename(self.docfile.name)

    def delete(self, *args, **kwargs):
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.docfile.name))
        except:
            pass
        super(DataDocument,self).delete(*args,**kwargs)

    def getcontent(self):
        with open(settings.MEDIA_ROOT + str(self.docfile), newline='') as csvfile:
            data = list(csv.reader(csvfile))
        return data

class OptModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length = 100, default = 'New Model')
    status = models.CharField(max_length = 50, default = 'DATA REQUIRED')
    codepath = models.CharField(max_length = 200, default = '')
    date_create = models.DateTimeField('date created')
    type  = models.IntegerField(default = 0)
    finished_steps = models.CharField(max_length = 10, default = '')
    notes = models.CharField(default = '', max_length = 1000)

    # Data
    Faculties = ListTextField(base_field=models.CharField(max_length=10), default = [])
    Students = ListTextField(base_field=models.CharField(max_length=10), default = [])
    Talks = ListTextField(base_field=models.CharField(max_length=10), default = [])
    Events = ListTextField(base_field=models.CharField(max_length=10), default = [])
    Periods = ListTextField(base_field=models.CharField(max_length=10), default = [])

    LowerLimit = ListTextField(base_field=models.CharField(max_length=10), default = [])
    UpperLimit = ListTextField(base_field=models.CharField(max_length=10), default = [])
    Duration = ListTextField(base_field=models.CharField(max_length=10), default = [])

    p_val = models.IntegerField(default = 10)
    n_val = models.IntegerField(default = 3)
    t_val = models.IntegerField(default = 5)

    FacultyTime = ListTextField(base_field=models.CharField(max_length=10), default = [])
    TalkTime = ListTextField(base_field=models.CharField(max_length=10), default = [])
    TalkPref = ListTextField(base_field=models.CharField(max_length=10), default = [])
    StudentsPref = ListTextField(base_field=models.CharField(max_length=10), default = [])
    EventsTime = ListTextField(base_field=models.CharField(max_length=10), default = [])
    ActivityCapacity = ListTextField(base_field=models.CharField(max_length=10), default = [])

    Rooms = ListTextField(base_field=models.CharField(max_length=10), default = [])
    FacultyNeedRoom = ListTextField(base_field=models.CharField(max_length=10), default = [])
    RoomCapacity = ListTextField(base_field=models.CharField(max_length=10), default = [])
    RoomTime = ListTextField(base_field=models.CharField(max_length=10), default = [])

    ResultsFaculty = ListTextField(base_field=models.CharField(max_length=10), default = [])
    ResultsStudent = ListTextField(base_field=models.CharField(max_length=10), default = [])
    ResultsRoom = ListTextField(base_field=models.CharField(max_length=10), default = [])

    ResultsFacultyFileLoc = models.CharField(max_length = 200, default = '')
    ResultsStudentFileLoc = models.CharField(max_length = 200, default = '')

    def __str__(self):
        return str(self.name)

    def writedatafiles(self):
        user = self.user
        task_id = self.id
        # remove existing files
        userfolder = settings.MEDIA_ROOT + str(user.id) + '_' + user.username
        try:
            os.stat(userfolder)
        except:
            os.mkdir(userfolder)

        folder = settings.MEDIA_ROOT + str(user.id) + '_' + user.username + '/model_' + str(self.id) + '/'
        try:
            os.stat(folder)
        except:
            os.mkdir(folder)

        for root, dirs, files in os.walk(folder):
            for filename in files:
                ff = folder + filename
                os.remove(ff)

        if len(self.FacultyTime) > 0:
            with open(folder + 'Faculty_time.csv', 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(['#']+self.Faculties)
                num_faculty = len(self.Faculties)
                for t in range(len(self.Periods)):
                    row = [self.Periods[t]]+self.FacultyTime[t*num_faculty:(t+1)*num_faculty]
                    writer.writerow(row)

        if len(self.StudentsPref) > 0:
            with open(folder + 'Student_pref.csv', 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(['Name']+self.Students)
                num_students = len(self.Students)
                for f in range(len(self.Faculties)):
                    row = [self.Faculties[f]]+self.StudentsPref[f*num_students:(f+1)*num_students]
                    writer.writerow(row)

        if len(self.TalkTime) > 0:
            with open(folder + 'Talk_time.csv', 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(['#']+self.Talks)
                num_talks = len(self.Talks)
                for t in range(len(self.Periods)):
                    row = [self.Periods[t]]+self.TalkTime[t*num_talks:(t+1)*num_talks]
                    writer.writerow(row)

        if len(self.TalkPref) > 0:
            with open(folder + 'Talk_pref.csv', 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                writer.writerow(['Name']+self.Students)
                num_students = len(self.Students)
                for f in range(len(self.Talks)):
                    row = [self.Talks[f]]+self.TalkPref[f*num_students:(f+1)*num_students]
                    writer.writerow(row)

        if len(self.ActivityCapacity) > 0:
            with open(folder + 'num_limit.csv', 'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                row = ["#"]
                if len(self.Faculties) > 0:
                    row += self.Faculties
                if len(self.Talks) > 0:
                    row += self.Talks
                rowlen = len(row)-1
                writer.writerow(row)
                writer.writerow(["lower"] + self.ActivityCapacity[0:rowlen])
                writer.writerow(["upper"] + self.ActivityCapacity[rowlen:2*rowlen])

        if len(self.Duration) > 0:
            with open(folder + 'num_limit.csv' ,'w') as csvfile:
                writer = csv.writer(csvfile, delimiter=',')
                row = ["#"]
                if len(self.Faculties) > 0:
                    row += self.Faculties
                writer.writerow(row)

                row = ["lower bound"]
                if len(self.LowerLimit) > 0:
                    row += self.LowerLimit
                writer.writerow(row)

                row = ["upper bound"]
                if len(self.UpperLimit) > 0:
                    row += self.UpperLimit
                writer.writerow(row)

                row = ["duration"]
                row += self.Duration
                writer.writerow(row)


    def readFacultyResults(self):
        task_id = self.id
        user = self.user
        folder = settings.MEDIA_ROOT + str(user.id) + '_' + user.username + '/model_' + str(self.id) + '/'
        with open(folder + 'results_pro.csv', newline='') as csvfile:
            data = list(csv.reader(csvfile))
        linedata = [data[i][j] for i in range(len(data)) for j in range(len(data[0]))]
        return linedata

    def readStudentResults(self):
        task_id = self.id
        user = self.user
        folder = settings.MEDIA_ROOT + str(user.id) + '_' + user.username + '/model_' + str(self.id) + '/'
        with open(folder + 'results_stu.csv', newline='') as csvfile:
            data = list(csv.reader(csvfile))
        linedata = [data[i][j] for i in range(len(data)) for j in range(len(data[0]))]
        return linedata

    def readTaskStatus(self):
        task_id = self.id
        user = self.user
        folder = settings.MEDIA_ROOT + str(user.id) + '_' + user.username + '/model_' + str(self.id) + '/'
        with open(folder + 'model_status.csv', newline='') as csvfile:
            data = list(csv.reader(csvfile))
        status = data[1][1]
        return status

    def delete(self, *args, **kwargs):
        task_id = self.id
        user = self.user
        folder = settings.MEDIA_ROOT + str(user.id) + '_' + user.username + '/model_' + str(self.id) + '/'
        try:
            shutil.rmtree(folder)
        except Exception as e:
            print(e)
        super(OptModel,self).delete(*args,**kwargs)
