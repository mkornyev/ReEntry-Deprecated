# IMPORTS

from django import forms
from django.contrib.auth import authenticate
from django.db import models
import re # Regex matching
import django_filters

from NewEra.models import User, CaseLoadUser, Resource, Tag, Referral
# CheckboxSelectMultiple widget from https://chase-seibert.github.io/blog/2010/05/20/django-manytomanyfield-on-modelform-as-checkbox-widget.html
from django.forms.widgets import CheckboxSelectMultiple

INPUT_ATTRIBUTES = {'class' : 'form-control'}
MAX_UPLOAD_SIZE = 2500000

# Model Forms

'''
COMMON NOTES:
- First names have a 30-digit maximum to match Django's maximum for first names
- Last names have a 150-digit maximum to match Django's maximum for last names
- Emails have a 254-digit maximum to reflect the IETF standard (https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address)
- Phone numbers have an 11-digit maximum to match a 1 and 10 subsequent digits at maximum (methods check for a minimum of 10 digits)
'''

# Form used to create and edit a CaseLoadUser
class CaseLoadUserForm(forms.ModelForm):
	# Set up attributes
	first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES), required=False)
	email = forms.EmailField(max_length=254, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES), required=False)
	nickname = forms.CharField(max_length=100, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES), required=False)
	notes = forms.CharField(max_length=1000, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES), required=False)

	# Define the model and fields to include/exclude
	class Meta:
		model = CaseLoadUser
		fields = ['first_name', 'last_name', 'nickname', 'email', 'phone', 'notes', 'is_active', 'user']
		exclude = (
			'user',
		)
		# Textarea widget used to more easily enter notes
		widgets = {
            'notes': forms.Textarea(attrs={'cols': 120, 'rows': 30}),
        }

	def __init__(self, *args, **kwargs):
		super(CaseLoadUserForm, self).__init__(*args, **kwargs)
		# is_active field not defined above so it can be hidden on creation; if the case load user exists, is_active
		self.fields['is_active'].widget.attrs=INPUT_ATTRIBUTES
		
		# Hide the is_active field if the model is being created
		# https://stackoverflow.com/questions/55994307/exclude-fields-for-django-model-only-on-creation
		if not self.instance or self.instance.pk is None:
			for name, field in self.fields.items():
				if name in ['is_active', ]:
					field.widget = forms.HiddenInput()

	# Validate the phone number entered
	def clean_phone(self):
		# Obtain only the digits entered from the phone
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		# Validate that the phone number is either the standard 10 digits or it is 11 starting with a 1
		if phone and (len(cleaned_phone) != 10 and not (len(cleaned_phone) == 11 and cleaned_phone[0] == '1')):
			raise forms.ValidationError('The phone number must be either exactly 10 digits or a 1 followed by 10 digits.')

		return cleaned_phone

	# Ensure that for a case load entry, the SOW has inputted values for either the phone or the email, or both
	def clean(self):
		# cleaned_data is necessary to get the fields after they've already been cleaned
		cleaned_data = super().clean()
		phone = cleaned_data.get('phone')
		email = cleaned_data.get('email')

		# Raise an error if neither field is valid
		if not (phone or email):
			raise forms.ValidationError('You must input either a phone number or an email address for this user.')

		return cleaned_data


# Form to edit users 
class EditUserForm(forms.ModelForm):
	# Set up attributes
	email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs=INPUT_ATTRIBUTES))
	first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	is_active = forms.BooleanField(required=False)

	# Define the model and fields to include/exclude
	class Meta:
		model = User
		fields = ('email', 'first_name', 'last_name', 'phone', 'is_active')
		exclude = (
			# A user's username cannot be changed
			'username',
			# A user's password and confirmation cannot be changed except through the change password link
			'password',
			'confirm_password'
		)

	# Validate the phone number entered
	def clean_phone(self):
		# Obtain only the digits entered from the phone
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		# Validate that the phone number is either the standard 10 digits or it is 11 starting with a 1
		if phone and (len(cleaned_phone) != 10 and not (len(cleaned_phone) == 11 and cleaned_phone[0] == '1')):
			raise forms.ValidationError('The phone number must be either exactly 10 digits or a 1 followed by 10 digits.')

		return cleaned_phone


# Form to edit the current, logged in user
class EditSelfUserForm(forms.ModelForm):
	# Set up attributes
	email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs=INPUT_ATTRIBUTES))
	first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	last_name  = forms.CharField(max_length=150, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	
	# Define the model and fields to include/exclude
	class Meta:
		model = User
		fields = ('email', 'first_name', 'last_name', 'phone')
		exclude = (
			# A user's username cannot be changed
			'username',
			# A user's password and confirmation cannot be changed except through the change password link
			'password',
			'confirm_password',
			# A user cannot make themselves inactive
			'is_active'
		)

	# Validate the phone number entered
	def clean_phone(self):
		# Obtain only the digits entered from the phone
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		# Validate that the phone number is either the standard 10 digits or it is 11 starting with a 1
		if phone and (len(cleaned_phone) != 10 and not (len(cleaned_phone) == 11 and cleaned_phone[0] == '1')):
			raise forms.ValidationError('The phone number must be either exactly 10 digits or a 1 followed by 10 digits.')

		return cleaned_phone


# Form to create and edit resources
class CreateResourceForm(forms.ModelForm):
	# Set up attributes
	name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	description = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(attrs=INPUT_ATTRIBUTES))
	is_active = forms.BooleanField(required=False)
	hours = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(attrs=INPUT_ATTRIBUTES))
	email = forms.EmailField(max_length=254, required=False, widget=forms.EmailInput(attrs=INPUT_ATTRIBUTES))
	phone = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	extension = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	street = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	street_secondary = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	zip_code = forms.CharField(max_length=10, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	state = forms.CharField(max_length=2, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	image = forms.FileField(label=('Image'),required=False, widget=forms.FileInput)
	url = forms.URLField(required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	contact_name = forms.CharField(max_length=181, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	contact_position = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	# Assuming fax number is like a phone number
	fax_number = forms.CharField(max_length=11, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	# This may or may not be different from the organizational email
	contact_email = forms.EmailField(max_length=254, required=False, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	# Define the model and fields to include/exclude
	class Meta:
		model = Resource
		fields = ('name', 'description', 'is_active', 'hours', 'email', 'phone', 'extension', 'street', 'street_secondary', 'city', 'state', 'zip_code', 'image', 'url', 'contact_name', 'contact_position', 'fax_number', 'contact_email', 'tags')
		# content_type is used to manage images, so the user should not manipulate it
		exclude = (
			'content_type',
		)

	def __init__(self, *args, **kwargs):
		super(CreateResourceForm, self).__init__(*args, **kwargs)
        # Tags field represented via the CheckboxSelectMultiple() widget
		self.fields['tags'].widget = CheckboxSelectMultiple()
		self.fields['tags'].queryset = Tag.objects.all()

		# Hide the is_active field if the model is being created
		# https://stackoverflow.com/questions/55994307/exclude-fields-for-django-model-only-on-creation
		if not self.instance or self.instance.pk is None:
			for name, field in self.fields.items():
				if name in ['is_active', ]:
					field.widget = forms.HiddenInput()

	# Validate the resource image
	def clean_image(self):
		image = self.cleaned_data['image']

		if image:
			# Raise an error if the file's extension isn't valid
			if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif', '.pdf')):
				raise forms.ValidationError('File type is not image')

			# Raise an error if the file isn't an image or if it is too large
			try:
				if (not image.content_type) or (not image.content_type.startswith('image')):
					raise forms.ValidationError('File type is not image')
				if image.size > MAX_UPLOAD_SIZE:
					raise forms.ValidationError('File too big (max: {0} mb)'.format(MAX_UPLOAD_SIZE/1000000))
			except:
				pass 

		return image

	# Validate the phone number entered
	def clean_phone(self):
		# Obtain only the digits entered from the phone
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		# Validate that the phone number is either the standard 10 digits or it is 11 starting with a 1
		if phone and (len(cleaned_phone) != 10 and not (len(cleaned_phone) == 11 and cleaned_phone[0] == '1') and not (len(cleaned_phone) == 3 and cleaned_phone[1] == '1' and cleaned_phone[2] == '1')):
			raise forms.ValidationError('The phone number must be either exactly 10 digits, a 1 followed by 10 digits, or an N-1-1 code of 3 digits.')

		return cleaned_phone

	# Validate the fax number entered
	def clean_fax_number(self):
		# Obtain only the digits entered from the fax
		fax_number = self.cleaned_data['fax_number']
		cleaned_fax_number = ''.join(digit for digit in fax_number if digit.isdigit())

		# Validate that the fax number is either the standard 10 digits or it is 11 starting with a 1
		if fax_number and (len(cleaned_fax_number) != 10 and not (len(cleaned_fax_number) == 11 and cleaned_fax_number[0] == '1')):
			raise forms.ValidationError('The fax number must be either exactly 10 digits or a 1 followed by 10 digits.')

		return cleaned_fax_number


# Form only used to edit notes
class EditReferralNotesForm(forms.ModelForm):
	# Notes is the only attribute SOWs can freely edit
	notes = forms.CharField(max_length=1000, required=False, widget=forms.Textarea(attrs=INPUT_ATTRIBUTES))

	# Define the model and fields to include/exclude
	class Meta:
		model = Referral
		fields = ('notes',)


# Form to create or edit tags
class TagForm(forms.ModelForm):
	# Name is the only attribute
	name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	# Define the model and fields to include/exclude
	class Meta:
		model = Tag
		fields = ('name',)


# Filter function for the resources; needs instantiation as a form
class ResourceFilter(django_filters.FilterSet):
	# Tags is the only attribute; uses the CheckboxSelectMultiple widget for easy selection
	tags = django_filters.ModelMultipleChoiceFilter(queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple, label='')

	# Define the model and fields to include/exclude
	class Meta:
		model = Resource
		fields = ('tags',)


# Standard Validation Forms 

# Form for a user to log in
class LoginForm(forms.Form):
	# Set up attributes; username and password are the only ones relevant for login
	username = forms.CharField(max_length=150, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs=INPUT_ATTRIBUTES))

	# Ensure that the username and password are valid
	def clean(self):
		# cleaned_data is necessary to get the fields after they've already been cleaned
		cleaned_data = super().clean()
		username = cleaned_data.get('username')
		password = cleaned_data.get('password')

		# Determine if a user exists with the given username and password
		user = authenticate(username=username, password=password)

		# Raise an error if the user does not exist
		if not user:
			raise forms.ValidationError("Invalid Username or Password Entered")

		return cleaned_data # Required by super


# Form for an admin to add a user
class RegistrationForm(forms.Form):
	# Set up attributes
	username = forms.CharField(max_length=150, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	password = forms.CharField(max_length=50, label='Password', widget=forms.PasswordInput(attrs=INPUT_ATTRIBUTES))
	confirm_password = forms.CharField(max_length=50, label='Confirm Password', widget=forms.PasswordInput(attrs=INPUT_ATTRIBUTES))
	email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs=INPUT_ATTRIBUTES))
	first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))
	phone = forms.CharField(max_length=11, widget=forms.TextInput(attrs=INPUT_ATTRIBUTES))

	# Define the model and fields to include/exclude
	class Meta:
		model = User
		fields = ['username', 'password', 'confirm_password' 'email', 'first_name', 'last_name', 'phone']
		# A user cannot make be made inactive when first created
		exclude = (
			'is_active',
		)

	# Ensure that the user's password is valid
	def clean(self):
		# cleaned_data is necessary to get the fields after they've already been cleaned
		cleaned_data = super().clean()
		password = cleaned_data.get('password')
		confirm_password = cleaned_data.get('confirm_password')

		# Raise an error if the password doesn't match the password_confirmation
		if password and confirm_password and password != confirm_password:
			raise forms.ValidationError("Passwords did not match.")

		return cleaned_data

	# Ensure that the username is not already used
	def clean_username(self):
		username = self.cleaned_data.get('username')

		# Raise an error if the username is already in the database
		if User.objects.filter(username__exact=username):
			raise forms.ValidationError("Username is already taken.")

		return username
		
	# Validate the phone number entered
	def clean_phone(self):
		# Obtain only the digits entered from the phone
		phone = self.cleaned_data['phone']
		cleaned_phone = ''.join(digit for digit in phone if digit.isdigit())

		# Validate that the phone number is either the standard 10 digits or it is 11 starting with a 1
		if phone and (len(cleaned_phone) != 10 and not (len(cleaned_phone) == 11 and cleaned_phone[0] == '1')):
			raise forms.ValidationError('The phone number must be either exactly 10 digits or a 1 followed by 10 digits.')

		return cleaned_phone
