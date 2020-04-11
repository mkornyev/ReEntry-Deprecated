"""ReEntryApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from NewEra import views

urlpatterns = [
    path('admin/', admin.site.urls), # Django Server route for entity management (avail to staff & superusers)

    # Url Routes for all users 
    path('', views.home, name='Home'),
    path('resources/', views.resources, name='Resources'),
    path('resources/<int:id>', views.get_resource, name = 'Show Resource'),
    path('image/<int:id>', views.get_resource_image, name = 'Image'), 
    path('login/', views.login, name = 'Login'),
    path('logout/', views.logout, name='Logout'),
    path('about/', views.about, name='About'),
    # path('register/', views.register, name = 'Register'),

    # Routes for SOWs 
    path('create_referral/', views.create_referral, name='Create Referral'),
    path('case_load/', views.case_load, name='Case Load'),

    # Routes for ADMINs 
    path('manage_users/', views.manage_users, name='Manage Users'),
    # User actions
    path('users/<int:id>/edit', views.edit_user, name='Edit User'),
    path('users/<int:id>/delete', views.delete_user, name='Delete User'),
    # Resource actions
    path('resources/new/', views.create_resource, name='Create Resource'),
    path('resources/<int:id>/edit/', views.edit_resource, name='Edit Resource'),
    path('resources/<int:id>/delete/', views.delete_resource, name='Delete Resource'),
    # Tag actions
    path('tags/', views.tags, name='Tags'),
    path('tags/new', views.create_tag, name='Create Tag'),
    path('tags/<int:id>/edit/', views.edit_tag, name='Edit Tag'),
    path('tags/<int:id>/delete/', views.delete_tag, name='Delete Tag'),
    # Referral actions
    path('referrals/', views.referrals, name='Referrals'),
    path('referrals/<int:id>/', views.get_referral, name='Show Referral'),
    # Case load actions
    path('case_load/<int:id>', views.get_case_load_user, name='Show Case Load User'),
    path('case_load/<int:id>/edit/', views.edit_case_load_user, name='Edit Case Load User'),
    path('case_load/<int:id>/delete/', views.delete_case_load_user, name='Delete Case Load User'),
    # Resource data export action
    path('export', views.export_data, name='Export Data')
]
