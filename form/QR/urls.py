from django.urls import  path, re_path, include
from . import views
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django_data_tables.utils import autodiscover as ddt_autodiscover
from django_data_tables import views as dt_views



ddt_autodiscover()
app_name = 'QR'

urlpatterns = [
    path('', views.registration_form, name='form'),
    #path('registration_form_teacher/', views.registration_form_teacher, name='form_teacher'),
    path('search/', views.search, name='search'),
    path('generate/<laptop_id>/', views.generate_qr_code, name='generate'),
    re_path(r'^login/$', views.user_login, name='user_login'),
    re_path(r'^logout/$', views.user_logout, name='user_logout'),
    path('home/', views.home, name='home'),
    path('faq/', views.faq, name='faq'),
    path('about/', views.about, name='about'),
    path('aboutt/', views.aboutt, name='aboutt'),
    re_path(r'^register/$', views.register, name='register'),
    path('owners/', views.list_owners, name='list_owners'),
    path('student-owners/', views.student_ownerlist, name='list_student_owners'),
    path('teachers-owners/', views.teachers_ownerlist, name='list_teacher_owners'),
    path('staff-owners/', views.staff_ownerlist, name='list_staff_owners'),


    path('owner/<int:owner_id>/', views.detail, name='detail'),

    
    #path(r'^password-reset/$', auth_views.password_reset, name="password_reset"),
    #path(r'^password-reset/done/$', auth_views.password_reset_done, name="password_reset_done"),
    #path(r'^password-reset/confirm/(?P<uidb64>[\w-]+)/(?P<token>[\w-]+)/$', auth_views.password_reset_confirm, name="password_reset_confirm"),
    #path(r'^password-reset/complete/$', auth_views.password_reset_complete, name="password_reset_complete"),
    path(r'^', include('django.contrib.auth.urls')),
]

