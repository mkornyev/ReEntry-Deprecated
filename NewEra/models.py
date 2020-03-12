from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate
from django.db import models
from django import forms

# NOTE: There is no validation in this model, as it seems like that should be done in forms (and it's hard to set up here)

# User model; extends AbstractUser
class User(AbstractUser):
	'''
	Fields taken care of by base User class in Django:
	- username
	- password
	- email
	- first_name
	- last_name

	Within this model, is_guest represents SOWs
	'''

	# 10 is the max length to force a phone number to be just the digits
	# We can change this later if needed
	phone = models.CharField(max_length=10, blank=False, null=False)

	# This shouldn't be necessary if we have is_staff and is_superuser
	'''
	# Create permitted roles
	# 	ROLE 	= "VALUE", _("Human readable name")
	class Role(models.TextChoices):
		ADMIN 	= "A", 	_("Admin")
		SOW		= "S", 	_("Street Outreach Worker")

	# Assign role
	role = modelsCharField(
		max_length = 1,
		choices = Role.choices,
		default = Role.SOW,
	)
	'''

	# city = 

	# Methods
	def __str__(self):
		return self.get_username() + " (" + self.get_full_name() + ")"

	def print_attributes(self):
		print("---\nUsername: " + self.get_username() + "\nFirst name: " + self.first_name + "\nLast name: " + self.last_name + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nActive:" + str(self.is_active) + "\nSuperuser: " + str(self.is_superuser) + "\nStaff: " + str(self.is_staff) + "\n---")

	def is_active_staff(self):
		return self.is_active and self.is_staff

	def get_case_load(self):
		return CaseLoadUser.objects.filter(user=self)

# Model for individuals on the case load
class CaseLoadUser(models.Model):
	# Attributes
	first_name = models.CharField(max_length=35, blank=False, null=False)
	last_name = models.CharField(max_length=35, blank=False, null=False)
	# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
	email = models.EmailField(max_length=254)
	# 10 is the max length to force a phone number to be just the digits
	# We can change this later if needed
	phone = models.CharField(max_length=10, null=False, blank=False)
	notes = models.CharField(max_length=1000)
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

	# Methods
	def __str__(self):
		return self.get_full_name() + ", phone number " + self.phone

	def get_full_name(self):
		return self.first_name + " " + self.last_name

	def print_attributes(self):
		print("---\nName: " + self.get_full_name() + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nNotes:\n" + self.notes + "\nUser: " + self.user.get_full_name() + "\n---")

# Model for an entire referral
class Referral(models.Model):
	# Attributes
	# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
	email = models.EmailField(max_length=254)
	# 10 is the max length to force a phone number to be just the digits
	# We can change this later if needed
	phone = models.CharField(max_length=10, blank=False, null=False)
	referral_date = models.DateField(auto_now=True)
	# resource_accessed = models.BooleanField()
	date_accessed = models.DateField(blank=True, null=True)
	notes = models.CharField(max_length=1000)

	# Foreign attributes
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
	caseUser = models.ForeignKey(CaseLoadUser, on_delete=models.CASCADE, blank=True, null=True)

	# Methods
	def __str__(self):
		# name = (first_name == None || last_name == None) ? self.get_full_name() : "(unknown)"
		return "Referral sent to " + self.phone + " by " + self.user.get_full_name() + " on " + self.referral_date.strftime("%m-%d-%Y")

	def print_attributes(self):
		print("---\nReferred by: " + self.user.get_full_name() + "\nReferred to: " + self.caseUser.phone + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nReferral date: " + self.referral_date.strftime("%m-%d-%Y") + "\nDate accessed: " + self.date_accessed.strftime("%m-%d-%Y") + "\nNotes: " + self.notes + "\n---")

# Model representing a tag
class Tag(models.Model):
	# Attributes
	name = models.CharField(max_length=20)

	# Methods
	def __str__(self):
		return self.name

	def print_attributes(self):
		print("---\nName: " + self.name + "\n---")

# Model representing one resource as it exists in isolation
class Resource(models.Model):
	# Attributes
	name = models.CharField(max_length=100, blank=False, null=False)
	description = models.CharField(max_length=1000)
	start_date = models.DateField(blank=True, null=True)
	end_date = models.DateField(blank=True, null=True)
	# !!! IMPORTANT !!!
	# Add regex validation for email and phone later
	# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
	email = models.EmailField(max_length=254)
	# 10 is the max length to force a phone number to be just the digits
	# We can change this later if needed
	phone = models.CharField(max_length=10)
	street = models.CharField(max_length=100)
	# This should account for 5-digit and 10-digit zip codes
	zip_code = models.CharField(max_length=10)
	# Refers to two digits
	state = models.CharField(max_length=2)
	image = models.FileField(blank=True)
	url = models.URLField()
	clicks = models.IntegerField(default=0)
	# city = models.BooleanField()

	# Many-to-many foreign keys
	tags = models.ManyToManyField(Tag)
	referrals = models.ManyToManyField(Referral)

	# Methods
	def __str__(self):
		return self.name

	def print_attributes(self):
		print("---\nName: " + self.name + "\nDescription: " + self.description + "\nStart Date: " + self.start_date.strftime("%m-%d-%Y") + "\nEnd date: " + self.end_date.strftime("%m-%d-%Y") + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nStreet: " + self.street + "\nZip code: " + self.zip_code + "\nState: " + self.state + "\nURL: " + self.url + "\nClicks: " + str(self.clicks) + "\n---")
