# IMPORTS

from django import forms
from django.contrib.auth import authenticate
from django.db import models
import re # Regex matching
import django_filters

from NewEra.models import User, CaseLoadUser, Resource, Tag, Referral
# Help from: https://chase-seibert.github.io/blog/2010/05/20/django-manytomanyfield-on-modelform-as-checkbox-widget.html
from django.forms.widgets import CheckboxSelectMultiple

INPUT_ATTRIBUTES = {'class' : 'form-control'}
MAX_UPLOAD_SIZE = 2500000

# Model Forms

class CaseLoadUserForm(forms.ModelForm):
	phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	nickname = forms.CharField(max_length=100, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	# Email currently is mandatory - need to change that
	# email = forms.CharField(max_length=50, widget = forms.EmailInput(attrs=INPUT_ATTRIBUTES), required=False)

	class Meta:
		model = CaseLoadUser
		fields = ['first_name', 'last_name', 'nickname', 'email', 'phone', 'notes', 'is_active', 'user']
		exclude = (
			'user',
		)
		widgets = {
            'notes': forms.Textarea(attrs={'cols': 120, 'rows': 30}),
        }

	def __init__(self, *args, **kwargs):
		super(CaseLoadUserForm, self).__init__(*args, **kwargs)
		self.fields['first_name'].widget.attrs=INPUT_ATTRIBUTES
		self.fields['last_name'].widget.attrs=INPUT_ATTRIBUTES
		self.fields['email'].widget.attrs=INPUT_ATTRIBUTES
		self.fields['notes'].widget.attrs=INPUT_ATTRIBUTES
		self.fields['is_active'].widget.attrs=INPUT_ATTRIBUTES
		
		# https://stackoverflow.com/questions/55994307/exclude-fields-for-django-model-only-on-creation
		if not self.instance or self.instance.pk is None:
			for name, field in self.fields.items():
				if name in ['is_active', ]:
					field.widget = forms.HiddenInput()

	def clean_phone(self):
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		if phone and (len(cleaned_phone) != 10 and not (len(cleaned_phone) == 11 and cleaned_phone[0] == '1')):
			raise forms.ValidationError('The phone number must be either exactly 10 digits or a 1 followed by 10 digits.')

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
	phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	class Meta:
		model = User
		fields = ['username', 'password', 'confirm_password' 'email', 'first_name', 'last_name', 'phone']
		exclude = (
			'is_active',
		)

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

		if phone and (len(cleaned_phone) != 10 and not (len(cleaned_phone) == 11 and cleaned_phone[0] == '1')):
			raise forms.ValidationError('The phone number must be either exactly 10 digits or a 1 followed by 10 digits.')

		return cleaned_phone


class EditUserForm(forms.ModelForm):
	email      = forms.CharField(max_length=50, widget = forms.EmailInput(attrs=INPUT_ATTRIBUTES))
	first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	last_name  = forms.CharField(max_length=50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
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

		if phone and (len(cleaned_phone) != 10 and not (len(cleaned_phone) == 11 and cleaned_phone[0] == '1')):
			raise forms.ValidationError('The phone number must be either exactly 10 digits or a 1 followed by 10 digits.')

		return cleaned_phone


class EditSelfUserForm(forms.ModelForm):
	email      = forms.CharField(max_length=50, widget = forms.EmailInput(attrs=INPUT_ATTRIBUTES))
	first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	last_name  = forms.CharField(max_length=50, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	
	class Meta:
		model = User
		fields = ('email', 'first_name', 'last_name', 'phone')
		exclude = (
			'username',
			'password',
			'confirm_password',
			'is_active'
		)

	def clean_phone(self):
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		if phone and (len(cleaned_phone) != 10 and not (len(cleaned_phone) == 11 and cleaned_phone[0] == '1')):
			raise forms.ValidationError('The phone number must be either exactly 10 digits or a 1 followed by 10 digits.')

		return cleaned_phone


class CreateResourceForm(forms.ModelForm):
	name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	description = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(attrs=INPUT_ATTRIBUTES))
	is_active = forms.BooleanField(required=False)
	hours = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(attrs=INPUT_ATTRIBUTES))
	email = forms.EmailField(max_length=254, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	phone = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	extension = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	street = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	street_secondary = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	zip_code = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	state = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	image = forms.FileField(label=('Image'),required=False, widget=forms.FileInput)
	url = forms.URLField(required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	contact_name = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	contact_position = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	# Assuming fax number is like a phone number
	fax_number = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	# This may or may not be different from the organizational email
	contact_email = forms.EmailField(max_length=254, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	class Meta:
		model = Resource
		fields = ('name', 'description', 'is_active', 'hours', 'email', 'phone', 'extension', 'street', 'street_secondary', 'city', 'state', 'zip_code', 'image', 'url', 'contact_name', 'contact_position', 'fax_number', 'contact_email', 'tags')
		exclude = (
			'content_type',
		)

	def __init__(self, *args, **kwargs):
        
		super(CreateResourceForm, self).__init__(*args, **kwargs)
        
		self.fields['tags'].widget = CheckboxSelectMultiple()
		self.fields['tags'].queryset = Tag.objects.all()

		# https://stackoverflow.com/questions/55994307/exclude-fields-for-django-model-only-on-creation
		if not self.instance or self.instance.pk is None:
			for name, field in self.fields.items():
				if name in ['is_active', ]:
					field.widget = forms.HiddenInput()

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

	def clean_phone(self):
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		if phone and (len(cleaned_phone) != 10 and not (len(cleaned_phone) == 11 and cleaned_phone[0] == '1')):
			raise forms.ValidationError('The phone number must be either exactly 10 digits or a 1 followed by 10 digits.')

		return cleaned_phone

	def clean_fax_number(self):
		fax_number = self.cleaned_data['fax_number']
		cleaned_fax_number = ''.join(digit for digit in fax_number if digit.isdigit())

		if fax_number and (len(cleaned_fax_number) != 10 and not (len(cleaned_fax_number) == 11 and cleaned_fax_number[0] == '1')):
			raise forms.ValidationError('The fax number must be either exactly 10 digits or a 1 followed by 10 digits.')

		return cleaned_fax_number


class TagForm(forms.ModelForm):
	name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	class Meta:
		model = Tag
		fields = ('name',)


# Filter function for the resources
class ResourceFilter(django_filters.FilterSet):
	tags = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple, label='')

	class Meta:
		model = Resource
		fields = ('tags',)


# Form only used to edit notes
class EditReferralNotesForm(forms.ModelForm):
	notes = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(attrs=INPUT_ATTRIBUTES))

	class Meta:
		model = Referral
		fields = ('notes',)
