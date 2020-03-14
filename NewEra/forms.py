# IMPORTS

from django import forms
from django.contrib.auth import authenticate
from django.db import models

from NewEra.models import User, Resource

# INPUT_ATTRIBUTES = {'style' : 'border: 1px solid gray; border-radius: 5px;'}
INPUT_ATTRIBUTES = {'class' : 'form-input'}



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


class CreateResourceForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True)
    description = forms.CharField(max_length=1000, widget=forms.Textarea(attrs=INPUT_ATTRIBUTES))
    email = forms.EmailField(max_length=254, required=False)
    phone = forms.CharField(max_length=10, required=False)
    street = forms.CharField(max_length=100, required=False)
    zip_code = forms.CharField(max_length=10, required=False)
    state = forms.CharField(max_length=2, required=False)
    url = forms.URLField(required=False)

    class Meta:
        model = Resource
        fields = ('name', 'description', 'start_date', 'end_date', 'email', 'phone', 'street', 'zip_code', 'state', 'image', 'url', 'tags')
