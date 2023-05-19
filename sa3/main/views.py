from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse
from django.conf import settings
from django.forms import formset_factory
from django.utils.encoding import smart_str
from wsgiref.util import FileWrapper
from django.db.models import Q
from functools import reduce
from .models import *
from .forms import *
import subprocess
import sys
from math import log
from collections import namedtuple
import numpy as np
import string
import random
import os
import io
import csv
import zipfile
import json
import operator
#import folium

from .utils import *

"""Home page"""
def main(request):
    return render(request, 'main.html')

def about(request):
	return render(request, 'about.html')

def contact(request):
	submitted = False
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			con = get_connection('django.core.mail.backends.console.EmailBackend')
			send_mail(
				cd['subject'],
				'From: ' + cd['email'] + '\n' + cd['message'],
				'online.opt.tool@gmail.com',
				['yichenghu1994@gmail.com'], # service email
				fail_silently = False)
			send_mail(
				'Message Received',
				'We have reveived your message and will respond to you soon!',
				'online.opt.tool@gmail.com',
				[cd['email']], # service email
				fail_silently = False)
			return HttpResponseRedirect('/contact?submitted=True')
	else:
		form = ContactForm()
		if 'submitted' in request.GET:
			submitted = True
		return render(request, 'contact.html', {'form': form, 'submitted': submitted})

# login page
def loginpage(request):
    formfail = 0
    authfail = 0
    if (request.POST.get('user_login')):
        uf = LoginForm(request.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            user = authenticate(username = username, password = password)
            if user is None:
                authfail = 1
                context = {'loginform': uf, 'formfail':formfail, 'authfail': authfail}
                return render(request, 'login.html', context)
            else:
                login(request,user)
                return redirect('main:dashboard')
        else:
            formfail = 1
            context = {'loginform': uf, 'formfail':formfail, 'authfail': authfail}
            return render(request, 'login.html', context)
    else:
        uf = LoginForm()
        context = {'loginform': uf, 'formfail': formfail,  'authfail': authfail}
        return render(request,'login.html', context)

# logout page, will redirect to expertmain
def logoutpage(request):
    user = request.user
    if user.is_authenticated:
        logout(request)
        return render(request, 'logout.html')
    else:
        redirect('main:main')


"""User Dashboard"""
@login_required()
def dashboard(request):
    user = request.user
    return render(request, 'dashboard.html', {'user': user})


"""User Profile Modification"""
@login_required()
def profile(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})

@login_required()
def userprofileedit(request):
    user = request.user
    if (request.POST):
        post_data = request.POST
        type = post_data['type']
        value = post_data['new_value']
        if type == 'First Name':
            user.first_name = value
            user.save()
        elif type == 'Last Name':
            user.last_name = value
            user.save()
        elif type == 'Email':
            user.email = value
            user.save()
        elif type == 'password':
            user.set_password(value)
            user.save()
            login(request, user)
        return JsonResponse({'success': True})
    else:
        return HttpResponse("Invalid request!")

"""Management of Models"""
@login_required()
def modellist(request):
    user = request.user
    tasklist = user.optmodel_set.all()
    return render(request, 'modellist.html', {'user': user, 'tasklist': tasklist})

@login_required()
def taskmanagedelete(request):
    user = request.user
    success = False
    if (request.POST):
        post_data = request.POST
        type = post_data['type']
        task_id = post_data['task_id']
        if 'delete_task' in type:
            task = user.optmodel_set.get(id = task_id)
            task.delete()
            success = True
        return JsonResponse({'success': success})
    else:
        return HttpResponse("Invalid request!")

@login_required()
def newmodel(request):
    user = request.user
    success = False
    if (request.POST):
        post_data = request.POST
        modelname = post_data['modelname']
        modelnotes = post_data['modelnotes'].replace("'"," ").replace('"',' ').replace('\n','')
        new_task = user.optmodel_set.create(name = modelname, date_create = timezone.now(), notes=modelnotes)
        new_task.save()
        success = True
        return JsonResponse({'success': success})
    else:
        return HttpResponse("Invalid request!")

@login_required()
def copymodel(request):
    user = request.user
    success = False
    if (request.POST):
        post_data = request.POST
        modelname = post_data['modelname']
        modelnotes = post_data['modelnotes'].replace("'"," ").replace('"',' ').replace('\n','')
        taskid = int(post_data['loadid'])
        new_task = OptModel.objects.get(pk =  taskid)
        new_task.pk = None
        new_task.save()

        new_task.ResultsFaculty = []
        new_task.ResultsStudent = []
        new_task.ResultsRoom = []
        new_task.ResultsFacultyFileLoc = []
        new_task.ResultsStudentFileLoc = []
        if '6' in new_task.finished_steps:
            new_task.finished_steps = new_task.finished_steps.replace('6','')

        new_task.status = 'DATA REQUIRED'
        new_task.name = modelname
        new_task.notes = modelnotes

        new_task.save()
        success = True
        return JsonResponse({'success': success})
    else:
        return HttpResponse("Invalid request!")

"""Model Home"""
@login_required()
def modelhome(request, model_id):
    user = request.user
    task = OptModel.objects.get(pk =  model_id)
    task_is_user = task in user.optmodel_set.all()
    fail = 0
    checked = 0
    msg = 0
    if not task_is_user:
        return redirect('main:loginpage')
    else:
        if (request.GET.get('see_results')):
            return redirect('expert:modelresults', task.id)
        else:
            return render(request, 'modelhome.html', {'user': user, 'task': task, 'fail': fail, 'checked': checked, 'message': msg})

"""Guidence for defining a problem"""
"""Step 1 - Model Type"""
@login_required()
def modelstep1(request, model_id):
    user = request.user
    task = OptModel.objects.get(pk = model_id)
    task_is_user = task in user.optmodel_set.all()
    if not task_is_user:
        return redirect('main:loginpage')
    else:
        if (request.GET.get('confirm_type')):
            mf = TaskTypeForm(request.GET)
            if mf.is_valid():
                task.type = int(mf.cleaned_data['model_type'])
                task.codepath = codeselector(task.type)
                if '1' not in task.finished_steps:
                    task.finished_steps += '1'
                task.save()
            return redirect('main:modelstep2', task.id)
        else:
            modelform = TaskTypeForm()
            return render(request, 'step1.html', {'user': user, 'task': task, 'modelform':modelform})

def modelstep2(request, model_id):
    user = request.user
    task = OptModel.objects.get(pk = model_id)
    task_is_user = task in user.optmodel_set.all()
    uf = DataUploadForm2()
    if not task_is_user:
        return redirect('main:loginpage')
    else:
        if len(task.Faculties):
            facultydata1 = task.Faculties
            facultydata2 = []
            num_faculty = len(facultydata1)
            for t in range(len(task.Periods)):
                row = [task.Periods[t]]+task.FacultyTime[t*num_faculty:(t+1)*num_faculty]
                facultydata2.append(row)
        else:
            facultydata1 = False
            facultydata2 = False
        return render(request, 'step2.html', {'user': user, 'task': task, 'dataform': uf, 'faculty': facultydata1, 'facultytime':facultydata2})

def step2dataupload(request):
    user = request.user
    if request.FILES:
        data = request.POST
        file = request.FILES
        new_data_file = user.datadocumentnew_set.create(docfile = file['datafile'], date_upload = timezone.now())
        new_data_file.save()
        modelid = int(request.POST['modelid'])
        task = OptModel.objects.get(pk = modelid)
        facultytimedata = new_data_file.getcontent()

        msg = facultytimeDataChecker(facultytimedata, task)
        if len(msg) > 0:
            success = False
        else:
            success = True

        new_data_file.delete()
        return JsonResponse({'success': success, 'msg': msg})
    else:
        return HttpResponse("Invalid request!")

def step2save(request):
    user = request.user
    if request.POST:
        data = request.POST
        modelid = int(request.POST['modelid'])
        task = OptModel.objects.get(pk = modelid)

        facultytimedata = json.loads(request.POST['dataframe'])

        msg = facultytimeDataChecker(facultytimedata, task)
        if len(msg) > 0:
            success = False
        else:
            success = True

        return JsonResponse({'success': success, 'msg': msg})
    else:
        return HttpResponse("Invalid request!")



def modelstep3(request, model_id):
    user = request.user
    task = OptModel.objects.get(pk = model_id)
    task_is_user = task in user.optmodel_set.all()
    uf = DataUploadForm2()
    if not task_is_user:
        return redirect('main:loginpage')
    else:
        if len(task.Students):
            studentdata1 = task.Students
            studentdata2 = []
            num_student = len(studentdata1)
            for t in range(len(task.Faculties)):
                row = [task.Faculties[t]]+task.StudentsPref[t*num_student:(t+1)*num_student]
                studentdata2.append(row)
        else:
            studentdata1 = False
            studentdata2 = False
        return render(request, 'step3.html', {'user': user, 'task': task, 'dataform': uf, 'student': studentdata1, 'studentpref':studentdata2})

def step3dataupload(request):
    user = request.user
    if request.FILES:
        data = request.POST
        file = request.FILES
        new_data_file = user.datadocumentnew_set.create(docfile = file['datafile'], date_upload = timezone.now())
        new_data_file.save()
        modelid = int(request.POST['modelid'])
        task = OptModel.objects.get(pk = modelid)
        studentprefdata = new_data_file.getcontent()

        msg = studentprefDataChecker(studentprefdata, task)
        if len(msg) > 0:
            success = False
        else:
            success = True

        new_data_file.delete()
        return JsonResponse({'success': success, 'msg': msg})
    else:
        return HttpResponse("Invalid request!")

def step3save(request):
    user = request.user
    if request.POST:
        data = request.POST
        modelid = int(request.POST['modelid'])
        task = OptModel.objects.get(pk = modelid)

        studentprefdata = json.loads(request.POST['dataframe'])

        msg = studentprefDataChecker(studentprefdata, task)
        if len(msg) > 0:
            success = False
        else:
            success = True

        return JsonResponse({'success': success, 'msg': msg})
    else:
        return HttpResponse("Invalid request!")

def modelstep4(request, model_id):
    user = request.user
    task = OptModel.objects.get(pk = model_id)
    task_is_user = task in user.optmodel_set.all()
    uf = DataUploadForm2()
    if not task_is_user:
        return redirect('main:loginpage')
    else:
        capacity = False
        if task.Duration:
            capacity = True
        return render(request, 'step4.html', {'user': user, 'task': task, 'dataform': uf, 'capacity': capacity})

def step4dataupload(request):
    user = request.user
    if request.FILES:
        data = request.POST
        file = request.FILES
        new_data_file = user.datadocumentnew_set.create(docfile = file['datafile'], date_upload = timezone.now())
        new_data_file.save()
        modelid = int(request.POST['modelid'])
        task = OptModel.objects.get(pk = modelid)
        capacitydata = new_data_file.getcontent()

        msg = capacitydataDataChecker(capacitydata, task)
        if len(msg) > 0:
            success = False
        else:
            success = True

        new_data_file.delete()
        return JsonResponse({'success': success, 'msg': msg})
    else:
        return HttpResponse("Invalid request!")

def step4save(request):
    user = request.user
    if request.POST:
        data = request.POST
        modelid = int(request.POST['modelid'])
        task = OptModel.objects.get(pk = modelid)

        capacitydata = json.loads(request.POST['dataframe'])

        msg = capacitydataDataChecker(capacitydata, task)
        if len(msg) > 0:
            success = False
        else:
            success = True

        return JsonResponse({'success': success, 'msg': msg})
    else:
        return HttpResponse("Invalid request!")

def modelstep5(request, model_id):
    user = request.user
    task = OptModel.objects.get(pk = model_id)
    task_is_user = task in user.optmodel_set.all()
    if not task_is_user:
        return redirect('main:loginpage')
    else:
        return render(request, 'step5.html', {'user': user, 'task': task})

def step5save(request):
    user = request.user
    if request.POST:
        data = request.POST
        modelid = int(request.POST['modelid'])
        task = OptModel.objects.get(pk = modelid)

        p_val = request.POST['p_val']
        n_val = request.POST['n_val']
        t_val = request.POST['t_val']

        msg = otherDataChecker(p_val, n_val, t_val, task)
        if len(msg) > 0:
            success = False
        else:
            success = True

        return JsonResponse({'success': success, 'msg': msg})
    else:
        return HttpResponse("Invalid request!")


def modelstep6(request, model_id):
    user = request.user
    task = OptModel.objects.get(pk = model_id)
    task_is_user = task in user.optmodel_set.all()
    if not task_is_user:
        return redirect('main:loginpage')
    else:
        return render(request, 'step6.html', {'user': user, 'task': task})

@login_required()
def beginsolve(request):
    user = request.user
    if request.POST:
        data = request.POST
        task_id = int(data['taskid'])
        task = OptModel.objects.get(pk = task_id)
        task.writedatafiles()
        msg = []
        success = True

        if '6' not in task.finished_steps:
            task.finished_steps += '6'

        cmd = ["/home/bitnami/julia-1.1.1/bin/julia", task.codepath, str(task.user.id), task.user.username, str(task.id), str(task.p_val), str(task.n_val), str(task.t_val)]
        print(cmd)
        p = subprocess.Popen(cmd, stderr=sys.stderr, stdout=sys.stdout)
        p.wait()

        task.ResultsFaculty = task.readFacultyResults()
        task.ResultsStudent = task.readStudentResults()
        task.status = task.readTaskStatus()

        task.ResultsFacultyFileLoc = settings.MEDIA_ROOT  + str(user.id) + '_' + user.username + '/model_' + str(task.id) + '/results_pro.csv'
        task.ResultsStudentFileLoc = settings.MEDIA_ROOT  + str(user.id) + '_' + user.username + '/model_' + str(task.id) + '/results_stu.csv'
        task.save()

        return JsonResponse({'msg': msg, 'success':success})
    else:
        return HttpResponse("Invalid request!")

def modelresults(request, model_id):
    user = request.user
    task = OptModel.objects.get(pk = model_id)
    task_is_user = task in user.optmodel_set.all()
    if not task_is_user:
        return redirect('main:loginpage')
    else:
        facultyresults = False
        studentresults = False
        if task.ResultsFacultyFileLoc and task.ResultsStudentFileLoc:
            with open(task.ResultsFacultyFileLoc, newline='') as csvfile:
                facultyresults = list(csv.reader(csvfile))
            with open(task.ResultsStudentFileLoc, newline='') as csvfile:
                studentresults = list(csv.reader(csvfile))
        return render(request, 'modelresults.html', {'user': user, 'task': task, 'facultyresults':facultyresults, 'studentresults':studentresults})
