# IMPORTS

from django import forms
from django.contrib.auth import authenticate
from django.db import models
import re # Regex matching
import django_filters

from NewEra.models import User, CaseLoadUser, Resource, Tag
# Help from: https://chase-seibert.github.io/blog/2010/05/20/django-manytomanyfield-on-modelform-as-checkbox-widget.html
from django.forms.widgets import CheckboxSelectMultiple

# INPUT_ATTRIBUTES = {'style' : 'border: 1px solid gray; border-radius: 5px;'}
INPUT_ATTRIBUTES = {'class' : 'form-input'}
MAX_UPLOAD_SIZE = 2500000

# Model Forms

class CaseLoadUserForm(forms.ModelForm):
	class Meta:
		model = CaseLoadUser
		fields = ['first_name', 'last_name', 'email', 'phone', 'notes', 'is_active', 'user']
		exclude = (
			'user',
		)

	def __init__(self, *args, **kwargs):
		super(CaseLoadUserForm, self).__init__(*args, **kwargs)
		self.fields['first_name'].widget.attrs=INPUT_ATTRIBUTES
		self.fields['last_name'].widget.attrs=INPUT_ATTRIBUTES
		self.fields['email'].widget.attrs=INPUT_ATTRIBUTES
		self.fields['phone'].widget.attrs=INPUT_ATTRIBUTES
		self.fields['notes'].widget.attrs=INPUT_ATTRIBUTES
		self.fields['is_active'].widget.attrs=INPUT_ATTRIBUTES

	def clean_phone(self):
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		if len(cleaned_phone) != 10:
			raise forms.ValidationError('You must enter a valid phone number')

		return cleaned_phone


# Standard Validation Forms 

class LoginForm(forms.Form):
	username = forms.CharField(max_length = 50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	password = forms.CharField(max_length = 50, widget=forms.PasswordInput(attrs=INPUT_ATTRIBUTES))

	def clean(self):
		cleaned_data = super().clean()
		username = cleaned_data.get('username')
		password = cleaned_data.get('password')

		user = authenticate(username=username, password=password)

		if not user:
			raise forms.ValidationError("Invalid Username or Password Entered")

		return cleaned_data # Required by super


class RegistrationForm(forms.Form):
	username   = forms.CharField(max_length = 50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	password  = forms.CharField(max_length = 50, label='Password', widget = forms.PasswordInput(attrs=INPUT_ATTRIBUTES))
	confirm_password  = forms.CharField(max_length = 50, label='Confirm Password', widget = forms.PasswordInput(attrs=INPUT_ATTRIBUTES))
	email      = forms.CharField(max_length=50, widget = forms.EmailInput(attrs=INPUT_ATTRIBUTES))
	first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	last_name  = forms.CharField(max_length=50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	phone = forms.CharField(max_length=10, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	def clean(self):
		cleaned_data = super().clean()
		password = cleaned_data.get('password')
		confirm_password = cleaned_data.get('confirm_password')

		if password and confirm_password and password != confirm_password:
			raise forms.ValidationError("Passwords did not match.")

		return cleaned_data

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username__exact=username):
			raise forms.ValidationError("Username is already taken.")

		return username
		
	def clean_phone(self):
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		if len(cleaned_phone) != 10:
			raise forms.ValidationError('You must enter a valid phone number')

		return cleaned_phone


class EditUserForm(forms.ModelForm):
	email      = forms.CharField(max_length=50, widget = forms.EmailInput(attrs=INPUT_ATTRIBUTES))
	first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	last_name  = forms.CharField(max_length=50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	phone = forms.CharField(max_length=10, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	is_active = forms.BooleanField(required=False)

	class Meta:
		model = User
		fields = ('email', 'first_name', 'last_name', 'phone', 'is_active')
		exclude = (
			'username',
			'password',
			'confirm_password'
		)

	def clean_phone(self):
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		if len(cleaned_phone) != 10:
			raise forms.ValidationError('You must enter a valid phone number.')

		return cleaned_phone


class CreateResourceForm(forms.ModelForm):
	name = forms.CharField(max_length=100, required=True)
	description = forms.CharField(max_length=1000, widget=forms.Textarea(attrs=INPUT_ATTRIBUTES))
	is_active = forms.BooleanField(required=False)
	hours = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(attrs=INPUT_ATTRIBUTES))
	email = forms.EmailField(max_length=254, required=False)
	phone = forms.CharField(max_length=11, required=False)
	extension = forms.CharField(max_length=11, required=False)
	street = forms.CharField(max_length=100, required=False)
	street_secondary = forms.CharField(max_length=100, required=False)
	city = forms.CharField(max_length=100)
	zip_code = forms.CharField(max_length=10, required=False)
	state = forms.CharField(max_length=2, required=False)
	url = forms.URLField(required=False)

	contact_name = forms.CharField(max_length=100, required=False)
	contact_position = forms.CharField(max_length=100, required=False)
	# Assuming fax number is like a phone number
	fax_number = forms.CharField(max_length=10, required=False)
	# This may or may not be different from the organizational email
	contact_email = forms.EmailField(max_length=254, required=False)

	class Meta:
		model = Resource
		fields = ('name', 'description', 'is_active', 'hours', 'email', 'phone', 'street', 'street_secondary', 'city', 'state', 'zip_code', 'image', 'url', 'contact_name', 'contact_position', 'fax_number', 'contact_email', 'tags')
		exclude = (
			'content_type',
		)

	def __init__(self, *args, **kwargs):
        
		super(CreateResourceForm, self).__init__(*args, **kwargs)
        
		self.fields['tags'].widget = CheckboxSelectMultiple()
		self.fields['tags'].queryset = Tag.objects.all()

	def clean_image(self):
		image = self.cleaned_data['image']

		if image:
			if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
				raise forms.ValidationError('File type is not image')

			try:
				if (not image.content_type) or (not image.content_type.startswith('image')):
					raise forms.ValidationError('File type is not image')
				if image.size > MAX_UPLOAD_SIZE:
					raise forms.ValidationError('File too big (max: {0} mb)'.format(MAX_UPLOAD_SIZE/1000000))
			except:
				pass 
		return image


class TagForm(forms.ModelForm):
	name = forms.CharField(max_length=20)

	class Meta:
		model = Tag
		fields = ('name',)


# Filter function for the resources
class ResourceFilter(django_filters.FilterSet):
	tags = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple, label='')

	class Meta:
		model = Resource
		fields = ('tags',)
