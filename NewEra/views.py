
# IMPORTS 

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login # 'login' can't clash w/view names in namespace 
from django.contrib.auth import logout as auth_logout # 'logout' can't clash w/view names in namespace 

from django.utils import timezone

from django.contrib.auth.models import User

# from NewEra.models import User, Resource, 
from NewEra.forms import LoginForm, RegistrationForm

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
	context = {} 
	#TEMP HTML TEMPLATE
	return render(request, 'NewEra/resources.html', context)