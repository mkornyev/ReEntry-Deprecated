
# IMPORTS 

import ast
import os

from django.http import Http404, HttpResponse, HttpResponseRedirect #, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login # 'login' can't clash w/view names in namespace 
from django.contrib.auth import logout as auth_logout # 'logout' can't clash w/view names in namespace 
from django.contrib import messages

from django.utils import timezone

from NewEra.models import User, CaseLoadUser, Resource, Referral, Tag
from NewEra.forms import LoginForm, RegistrationForm, CaseLoadUserForm, CreateResourceForm, TagForm, ResourceFilter

# VIEW ACTIONS 

def home(request): 
	context = {}
	return render(request, 'NewEra/index.html', context)

def resources(request):
	all_resources = Resource.objects.all()

	context = {
		'resources': all_resources,
		'active_resources': all_resources.filter(is_active=True),
		'inactive_resources': all_resources.filter(is_active=False),
		'tags': Tag.objects.all()
	}

	context['filter'] = ResourceFilter(request.GET, queryset=context['resources'])

	if request.method == 'GET':
		context['active_resources'] = context['filter'].qs.filter(is_active=True)
		context['inactive_resources'] = context['filter'].qs.filter(is_active=False)

	return render(request, 'NewEra/resources.html', context)

def get_resource(request, id):
	resource = get_object_or_404(Resource, id=id)
	context = { 'resource': resource, 'tags': resource.tags.all() }
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
		return render(request, 'NewEra/login.html', context)

	user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password'])

	auth_login(request, user)
	return redirect(reverse('Home'))

@login_required
def logout(request):
	auth_logout(request)
	return redirect(reverse('Login'))

def about(request):
	return render(request, 'NewEra/about.html')

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
				resource.content_type = form.cleaned_data['image'].content_type

				# REMOVE OLD IMAGE (for edit action)
				# if oldImageName: 
				# 	BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
				# 	IMAGE_ROOT = os.path.join(BASE_DIR, 'socialnetwork/user_uploads/' + oldImageName.name)
				# 	os.remove(IMAGE_ROOT)

			form.save()
			resource.save()

			messages.success(request, 'Form submission successful')

			return redirect('Resources')
	else:
		form = CreateResourceForm()

	return render(request, 'NewEra/edit_resource.html', context)

# SOW Actions 

def create_referral(request):
	resources = request.GET.get('resources', None)	

	if request.method == 'GET' and resources:
		resources = [digit.strip() for digit in ast.literal_eval(resources)] # Safely parse array
		resources = [ get_object_or_404(Resource, id=resourceId) for resourceId in resources ]

		recipients = [] 
		if request.user.is_superuser: 
			recipients = CaseLoadUser.objects.all()
		elif request.user.is_staff: 
			recipients = recipients = CaseLoadUser.objects.filter(user=request.user)

		return render(request, 'NewEra/create_referral.html', {'resources': resources, 'recipients': recipients})
	elif request.method == 'POST' and 'user_id' in request.POST and 'notes' in request.POST:
		caseload_user = get_object_or_404(CaseLoadUser, id=request.POST['user_id'])
		resources = [get_object_or_404(Resource, id=num) for num in request.POST.getlist('resources[]')]

		referral = Referral(email='', phone='', notes=request.POST['notes'], user=request.user, caseUser=caseload_user)
		referral.save()

		for r in resources: 
			referral.resource_set.add(r)
		
		referral.sendNotifications()

	return redirect(reverse('Resources'))

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
	context['action'] = 'Create'

	if request.method == 'POST':
		resource = Resource()
		form = CreateResourceForm(request.POST, request.FILES, instance=resource)
		
		if form.is_valid():
			# Update content_type
			pic = form.cleaned_data['image']
			if pic and pic != '':
				print('Uploaded image: {} (type={})'.format(pic, type(pic)))
				resource.content_type = form.cleaned_data['image'].content_type

			form.save()
			resource.save()

			messages.success(request, 'Resource successfully created!')

			return redirect('Resources')
	else:
		form = CreateResourceForm()

	return render(request, 'NewEra/edit_resource.html', context)

def edit_resource(request, id):
	resource = get_object_or_404(Resource, id=id)
	oldImage = resource.image

	if request.method == "POST":
		form = CreateResourceForm(request.POST, request.FILES, instance=resource)
    
		if form.is_valid():

			pic = form.cleaned_data['image']
			if pic and pic != '':
				
				# Update content type, remove old image
				try: 
					# Edge case where revalidated file is a FieldFile type (and not an Image)
					resource.content_type = form.cleaned_data['image'].content_type
					deleteImage(oldImage)
				except: 
					pass

			form.save()
			resource.save()

			return redirect('Show Resource', id=resource.id)
	else:
		form = CreateResourceForm(instance=resource)
	return render(request, 'NewEra/edit_resource.html', {'form': form, 'resource': resource, 'action': 'Edit'})

def delete_resource(request, id):
	resource = get_object_or_404(Resource, id=id)

	if request.method == 'POST':
		if (resource.referrals.count() == 0):
			deleteImage(resource.image)
			resource.delete()
			messages.success(request, 'Resource successfully deleted.')
			return redirect('Resources')
		else:
			resource.is_active = False
			resource.save()
			messages.success(request, 'Resource was made inactive.')
			return redirect('Show Resource', id=resource.id)
	return render(request, 'NewEra/delete_resource.html', {'resource': resource})

# Deletes the given image if it exists
def deleteImage(oldImage):
	if oldImage: 
		BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		IMAGE_ROOT = os.path.join(BASE_DIR, 'NewEra/user_uploads/' + oldImage.name)
		os.remove(IMAGE_ROOT)

# Creates tags
def tags(request):
	context = {
		'tags': Tag.objects.all()
	}
	return render(request, 'NewEra/tags.html', context)

def create_tag(request):
	context = {}
	form = TagForm()
	context['form'] = form
	context['action'] = 'Create'

	if request.method == 'POST':
		tag = Tag()
		form = TagForm(request.POST, instance=tag)
		
		if form.is_valid():
			form.save()
			tag.save()

			messages.success(request, 'Tag successfully created!')

			return redirect('Tags')
	else:
		tag = TagForm()

	return render(request, 'NewEra/edit_tag.html', context)

def edit_tag(request, id):
	tag = get_object_or_404(Tag, id=id)

	if request.method == "POST":
		form = TagForm(request.POST, instance=tag)
    
		if form.is_valid():
			form.save()
			tag.save()

			return redirect('Tags')
	else:
		form = TagForm(instance=tag)
	return render(request, 'NewEra/edit_tag.html', {'form': form, 'tag': tag, 'action': 'Edit'})

def delete_tag(request, id):
	tag = get_object_or_404(Tag, id=id)

	if request.method == 'POST':
		tag.delete()
		messages.success(request, 'Tag successfully deleted.')
		return redirect('Tags')

	return render(request, 'NewEra/delete_tag.html', {'tag': tag})
