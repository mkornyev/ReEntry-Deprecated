
# IMPORTS 

from django.http import Http404 #, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login # 'login' can't clash w/view names in namespace 
from django.contrib.auth import logout as auth_logout # 'logout' can't clash w/view names in namespace 

from django.utils import timezone

from NewEra.models import User, CaseLoadUser
from NewEra.forms import LoginForm, RegistrationForm, CaseLoadUserForm

# VIEW ACTIONS 

def home(request): 
	context = {}
	return render(request, 'NewEra/index.html', context)

def resources(request):
	context = {}
	return render(request, 'NewEra/resources.html', context)

def get_resource(request, id):
	# resource = get_object_or_404(Resource, id=id)
	# context = { 'resource': resource }
	context = {} 
	return render(request, 'NewEra/get_resource.html', context)

def login(request):
	if request.user.is_authenticated:
		return redirect(reverse('Home'))

	context = {} 
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
	context = {} 
	# TEMP HTML TEMPLATE
	return render(request, 'NewEra/resources.html', context)

def case_load(request):
	users = [] 

	if request.user.is_superuser: 
		users = CaseLoadUser.objects.all()	
	elif request.user.is_staff:
		users = CaseLoadUser.objects.filter(user=request.user) 
	else:  
		raise Http404

	context = {'caseload_users': users, 'form': CaseLoadUserForm()} 
	#TEMP HTML TEMPLATE
	return render(request, 'NewEra/resources.html', context)


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

	
