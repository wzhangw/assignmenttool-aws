from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate
from django.conf import settings
import csv

class ContactForm(forms.Form):
    yourname = forms.CharField(
        required=True,
        label='Name',
        widget = forms.TextInput(attrs = {'class':'form-control'}))
    email = forms.EmailField(
        required=True,
        label='E-mail',
        widget = forms.TextInput(attrs = {'class':'form-control'}))
    subject = forms.CharField(
        required=True,
        label = 'Subject',
        widget = forms.TextInput(attrs = {'class':'form-control'}))
    message = forms.CharField(
        label = 'Content',
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 12}))

    def clean(self):
        name = self.cleaned_data['yourname']
        email = self.cleaned_data['email']
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']

class LoginForm(forms.Form):
    username = forms.CharField(
        label = "Username",
        widget = forms.TextInput(attrs = {'placeholder': 'Username', 'class':'form-control'}),
        required = True)
    password = forms.CharField(
        label = "Password",
        widget = forms.PasswordInput(attrs = {'placeholder': 'Password', 'class':'form-control'}),
        required = True)
    def clean(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            raise forms.ValidationError({'username': ["The username '%s' does not exist." % username]})
        else:
            pass

class DataUploadForm(forms.Form):
    datafile = forms.FileField(
            label='Upload a data file(.csv)',
            widget=forms.FileInput(attrs = {'class':'custom-file-input', 'onchange': 'UpdateLabel()'}),
            required = False
            )
    datanotes = forms.CharField(
            widget = forms.Textarea({'placeholder': 'Write your notes here', 'class':'form-control', 'rows': 6}),
            required = False
        )
    datatypes = (
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
    )
    datatype=forms.CharField(
        widget=forms.Select(choices=datatypes, attrs = {'class':'custom-select', 'onchange': 'UpdateTable()'})
    )

class DataUploadForm2(forms.Form):
    datafile = forms.FileField(
            label='Upload a data file(.csv)',
            widget=forms.FileInput(attrs = {'class':'custom-file-input', 'onchange': 'UpdateLabel()'}),
            required = False
            )

class TaskTypeForm(forms.Form):
    Model_Type_List = (
        #(1,'Scheduling'),
        #(2,'Scheduling and Room Assignment')
        (3,'Graduate Assignment'),
    )
    model_type=forms.IntegerField(
        widget=forms.Select(choices=Model_Type_List, attrs = {'class':'custom-select'})
    )
