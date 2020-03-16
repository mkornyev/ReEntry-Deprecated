
# IMPORTS 

from django.http import Http404, HttpResponse #, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login # 'login' can't clash w/view names in namespace 
from django.contrib.auth import logout as auth_logout # 'logout' can't clash w/view names in namespace 
from django.contrib import messages

from django.utils import timezone

from NewEra.models import User, CaseLoadUser, Resource
from NewEra.forms import LoginForm, RegistrationForm, CaseLoadUserForm, CreateResourceForm

import os

# VIEW ACTIONS 

def home(request): 
	context = {}
	return render(request, 'NewEra/index.html', context)

def resources(request):
	context = {
		'resources': Resource.objects.all(),
		'active_resources': Resource.objects.all().filter(is_active=True),
		'inactive_resources': Resource.objects.all().filter(is_active=False)
	}
	return render(request, 'NewEra/resources.html', context)

def get_resource(request, id):
	resource = get_object_or_404(Resource, id=id)
	context = { 'resource': resource }
	return render(request, 'NewEra/get_resource.html', context)

# ***** Note about images *****
# They are uploaded to the system as type .JPEG or .PNG etc.
# And then saved as type django.FileField() 
# *****************************
def get_resource_image(request, id): 
	resource = get_object_or_404(Resource, id=id)

	if not resource.image:
		raise Http404

	return HttpResponse(resource.image, content_type=resource.content_type)

def login(request):
	if request.user.is_authenticated:
		return redirect(reverse('Home'))

	context = {
		'resources': Resource.objects.all(),
		'active_resources': Resource.objects.all().filter(is_active=True),
		'inactive_resources': Resource.objects.all().filter(is_active=False)
	}
	if request.method == 'GET':
		context['form'] = LoginForm()
		return render(request, 'NewEra/login.html', context)

	form = LoginForm(request.POST)
	context['form'] = form

	if not form.is_valid():
		print(form.errors)
		return render(request, 'NewEra/login.html', context)

	user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password'])

	auth_login(request, user)
	return render(request, 'NewEra/resources.html', context)

@login_required
def logout(request):
	auth_logout(request)
	return redirect(reverse('Login'))

def about(request):
	return render(request, 'NewEra/about.html')


# SOW Actions 

def create_referral(request):
	context = {
		'resources': Resource.objects.all(),
		'active_resources': Resource.objects.all().filter(is_active=True),
		'inactive_resources': Resource.objects.all().filter(is_active=False)
	}
	# TEMP HTML TEMPLATE
	return render(request, 'NewEra/resources.html', context)

def case_load(request):
	users = [] 
	context = {} 

	if request.user.is_superuser: 
		users = CaseLoadUser.objects.all()	
		context['staff'] = User.objects.order_by('first_name', 'last_name')
	elif request.user.is_staff:
		users = CaseLoadUser.objects.filter(user=request.user).order_by('first_name', 'last_name')
	else:  
		raise Http404

	if request.method == 'POST' and 'staff_id' in request.POST:
		staff_user = get_object_or_404(User, id=request.POST['staff_id'])
		load_user = CaseLoadUser(user=staff_user)
		form = CaseLoadUserForm(request.POST, instance=load_user)

		if not form.is_valid():
			context['form'] = form 
			return render(request, 'NewEra/case_load.html', context)

		form.save()
		load_user.save() 

	context['caseload_users'] = users
	context['form'] = CaseLoadUserForm()
	return render(request, 'NewEra/case_load.html', context)


# ADMIN actions 

def manage_users(request): 
	if not request.user.is_superuser:
		raise Http404

	admins = User.objects.filter(is_superuser=True)
	sows = User.objects.filter(is_superuser=False).filter(is_staff=True)
	context = {'admins':admins, 'sows':sows, 'form': RegistrationForm()}

	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		context['form'] = form

		if not form.is_valid():
			return render(request, 'NewEra/manage_users.html', context)

		user = User.objects.create_user(username=form.cleaned_data['username'], 
										password=form.cleaned_data['password'],
										email=form.cleaned_data['email'],
										phone=form.cleaned_data['phone'],
										first_name=form.cleaned_data['first_name'],
										last_name=form.cleaned_data['last_name'])
		user.is_staff = True 
		user.is_superuser = False

		# Radio button input 
		if 'user_type' in request.POST and request.POST['user_type'] == 'admin': 
			user.is_superuser = True

		user.save()
	
	context['form'] = RegistrationForm()
	return render(request, 'NewEra/manage_users.html', context)

def create_resource(request):
	context = {}
	form = CreateResourceForm()
	context['form'] = form

	if request.method == 'POST':
		resource = Resource()
		form = CreateResourceForm(request.POST, request.FILES, instance=resource)
		
		if form.is_valid():
			# Update content_type
			pic = form.cleaned_data['image']
			if pic and pic != '':
				print('Uploaded image: {} (type={})'.format(pic, type(pic)))

				resource.content_type = form.cleaned_data['image'].content_type

				# REMOVE OLD IMAGE (for edit action)
				# if oldImageName: 
				# 	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
				# 	IMAGE_ROOT = os.path.join(BASE_DIR, 'socialnetwork/user_uploads/' + oldImageName.name)
				# 	os.remove(IMAGE_ROOT)

			form.save()
			resource.save()

			messages.success(request, 'Resource successfully created!')

			return redirect('Resources')
	else:
		form = CreateResourceForm()

	return render(request, 'NewEra/edit_resource.html', context)

def edit_resource(request, id):
	resource = get_object_or_404(Resource, id=id)
	oldImageName = resource.image

	if request.method == "POST":
		form = CreateResourceForm(request.POST or None, request.FILES, instance=resource)
		if form.is_valid():

			# Does not work, not sure why

			pic = form.cleaned_data['image']
			if pic and pic != '':
				print('Uploaded image: {} (type={})'.format(pic, type(pic)))

				resource.content_type = form.cleaned_data['image'].content_type

				if oldImageName: 
					BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
					IMAGE_ROOT = os.path.join(BASE_DIR, 'NewEra/user_uploads/' + oldImageName.name)
					os.remove(IMAGE_ROOT)

			form.save()
			resource.save()

			return redirect('Show Resource', id=resource.id)
	else:
		form = CreateResourceForm(instance=resource)
	return render(request, 'NewEra/edit_resource.html', {'form': form, 'resource': resource})

def delete_resource(request, id):
	resource = get_object_or_404(Resource, id=id)

	if request.method == 'POST':
		if (resource.referrals.count() == 0):
			resource.delete()
			messages.success(request, 'Resource successfully deleted.')
			return redirect('Resources')
		else:
			resource.is_active = False
			resource.save()
			messages.success(request, 'Resource was made inactive.')
			return redirect('Show Resource', id=resource.id)
	return render(request, 'NewEra/delete_resource.html', {'resource': resource})
