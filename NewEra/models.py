from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate
from django.db import models

# NOTE: There is no validation in this model, as it seems like that should be done in forms (and it's hard to set up here)

# User model; extends AbstractUser
class User(AbstractUser):
	'''
	Fields taken care of by base User class in Django:
	- username
	- password
	- email (overriden here)
	- first_name (overriden here)
	- last_name (overriden here)

	Within this model, is_guest represents SOWs
	'''

	# HOWEVER, we are going to require first_name and last_name for recordkeeping purposes
	first_name = models.CharField(max_length=30, blank=False, null=False)
	last_name = models.CharField(max_length=150, blank=False, null=False)

	# !!! IMPORTANT !!!
	# Add regex validation for email and phone later
	# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
	email = models.EmailField(max_length=254, blank=False, null=False)

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
		return CaseLoad.objects.filter(user=self)

# Model for individuals on the case load
class CaseLoad(models.Model):
	# Attributes
	first_name = models.CharField(max_length=35, blank=False, null=False)
	last_name = models.CharField(max_length=35, blank=False, null=False)
	# !!! IMPORTANT !!!
	# Add regex validation for email and phone later
	# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
	email = models.EmailField(max_length=254)
	# 10 is the max length to force a phone number to be just the digits
	# We can change this later if needed
	phone = models.CharField(max_length=10, null=False, blank=False)
	notes = models.CharField(max_length=1000)
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)

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
	# !!! IMPORTANT !!!
	# Add regex validation for email and phone later
	# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
	email = models.EmailField(max_length=254, blank=False, null=False)
	# 10 is the max length to force a phone number to be just the digits
	# We can change this later if needed
	phone = models.CharField(max_length=10, blank=False, null=False)
	referral_date = models.DateField(auto_now=True)
	# resource_accessed = models.BooleanField()
	date_accessed = models.DateField()
	notes = models.CharField(max_length=1000)

	# Foreign attributes
	user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
	case = models.ForeignKey(CaseLoad, on_delete=models.CASCADE)

	# Methods
	def __str__(self):
		# name = (first_name == None || last_name == None) ? self.get_full_name() : "(unknown)"
		return "Referral sent to " + self.phone + " by " + self.user.get_full_name() + " on " + str(self.referral_date)

	def print_attributes(self):
		print("---\nReferred by: " + self.user.get_full_name() + "\nReferred to: " + self.case.phone + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nReferral date: " + str(self.referral_date) + "\nDate accessed: " + str(self.date_accessed) + "\nNotes: " + self.notes + "\n---")

# Model representing one resource as it exists in isolation
class Resource(models.Model):
	# Attributes
	name = models.CharField(max_length=100, blank=False, null=False)
	description = models.CharField(max_length=1000)
	start_date = models.DateField()
	end_date = models.DateField()
	# !!! IMPORTANT !!!
	# Add regex validation for email and phone later
	# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
	email = models.EmailField(max_length=254, blank=False, null=False)
	# 10 is the max length to force a phone number to be just the digits
	# We can change this later if needed
	phone = models.CharField(max_length=10)
	street = models.CharField(max_length=100)
	# This should account for 5-digit and 10-digit zip codes
	zip_code = models.CharField(max_length=10)
	# Refers to two digits
	state = models.CharField(max_length=2)
	image = models.ImageField()
	url = models.URLField()
	clicks = models.IntegerField(default=0)
	# city = models.BooleanField()

	# Methods
	def __str__(self):
		return self.name

	def print_attributes(self):
		print("---\nName: " + self.name + "\nDescription: " + self.description + "\nStart Date: " + str(self.start_date) + "\nEnd date: " + str(self.end_date) + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nStreet: " + self.street + "\nZip code: " + self.zip_code + "\nState: " + self.state + "\nURL: " + self.url + "\nClicks: " + str(self.clicks) + "\n---")

# Model representing a tag
class Tag(models.Model):
	# Attributes
	name = models.CharField(max_length=20)

	# Methods
	def __str__(self):
		return self.name

	def print_attributes(self):
		print("---\nName: " + self.name + "\n---")

# Model capturing an individual referred resource
class ResourceReferral(models.Model):
	# Foreign attributes
	referral = models.ForeignKey(Referral, on_delete=models.CASCADE)
	resource = models.ForeignKey(Resource, on_delete=models.CASCADE)

	# Methods
	def __str__(self):
		return self.resource.name + " referred to:\n" + self.referral.phone

	def print_attributes(self):
		print("---\nReferral: " + self.referral.phone + "\nResource: " + self.resource.name + "\n---")

# Model capturing a tag as applied to a given resource
class ResourceTag(models.Model):
	# Attributes
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
	resource = models.ForeignKey(Resource, on_delete=models.CASCADE)

	# Methods
	def __str__(self):
		return self.resource.name + " has tag " + self.tag.name

	def print_attributes(self):
		print("---\nTag: " + self.tag.name + "\nResource: " + self.resource.name + "\n---")
