from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.main, name = 'main'),
    path('about', views.about, name = 'about'),
    path('contact', views.contact, name = 'contact'),
    path('login', views.loginpage, name = 'loginpage'),
    path('logout', views.logoutpage, name = 'logoutpage'),
    path('dashboard', views.dashboard, name = 'dashboard'),
    path('profile', views.profile, name = 'profile'),
    path('ajax/userprofileedit', views.userprofileedit, name = 'userprofileedit'),
    path('ajax/step2dataupload', views.step2dataupload, name = 'step2dataupload'),
    path('ajax/step2save', views.step2save, name = 'step2save'),
    path('ajax/step3dataupload', views.step3dataupload, name = 'step3dataupload'),
    path('ajax/step3save', views.step3save, name = 'step3save'),
    path('ajax/step4dataupload', views.step4dataupload, name = 'step4dataupload'),
    path('ajax/step4save', views.step4save, name = 'step4save'),
    path('ajax/step5save', views.step5save, name = 'step5save'),
    #path('dashboard/datafiles', views.datafiles, name = 'datafiles'),
    #path('dashboard/ajax/renamefile', views.renamefile, name = 'renamefile'),
    #path('dashboard/ajax/renotefile', views.renotefile, name = 'renotefile'),
    #path('dashboard/ajax/deleteselectedfiles', views.deleteselectedfiles, name = 'deleteselectedfiles'),
    #path('dashboard/ajax/downloadselectedfiles', views.downloadselectedfiles, name = 'downloadselectedfiles'),
    #path('dashboard/ajax/dataupload', views.dataupload, name = 'dataupload'),
    path('dashboard/modellist', views.modellist, name = 'modellist'),
    path('dashboard/ajax/deletetask', views.taskmanagedelete, name = 'taskmanagedelete'),
    path('dashboard/ajax/newmodel', views.newmodel, name = 'newmodel'),
    path('dashboard/ajax/copymodel', views.copymodel, name = 'copymodel'),
    path('dashboard/modellist/<int:model_id>', views.modelhome, name = 'modelhome'),
    path('dashboard/modellist/<int:model_id>/1', views.modelstep1, name = 'modelstep1'),
    path('dashboard/modellist/<int:model_id>/2', views.modelstep2, name = 'modelstep2'),
    path('dashboard/modellist/<int:model_id>/3', views.modelstep3, name = 'modelstep3'),
    path('dashboard/modellist/<int:model_id>/4', views.modelstep4, name = 'modelstep4'),
    path('dashboard/modellist/<int:model_id>/5', views.modelstep5, name = 'modelstep5'),
    path('dashboard/modellist/<int:model_id>/6', views.modelstep6, name = 'modelstep6'),
    path('dashboard/modelist/beginsolving', views.beginsolve, name = 'beginsolve'),
    path('dashboard/modellist/<int:model_id>/results', views.modelresults, name = 'modelresults'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
