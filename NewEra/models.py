from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate
from django.db import models
from django import forms
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from datetime import datetime

# SMS carriers used for sending texts in a referral while deployed on Heroku
# Not needed when Twilio is integrated into the app
SMS_CARRIERS = {
	'AT&T':    '@txt.att.net',
	'TMobile':' @tmomail.net',
	'Verizon':  '@vtext.com',
	'Sprint':   '@page.nextel.com'
}

'''
COMMON NOTES:
- First names have a 30-digit maximum to match Django's maximum for first names
- Last names have a 150-digit maximum to match Django's maximum for last names
- Emails have a 254-digit maximum to reflect the IETF standard (https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address)
- Phone numbers have an 11-digit maximum to match a 1 and 10 subsequent digits at maximum (methods check for a minimum of 10 digits)
'''

# User model; extends Django's default AbstractUser
class User(AbstractUser):
	'''
	Fields taken care of by base User class in Django:
	- username
	- password
	- email
	- first_name
	- last_name

	Within this model, is_staff represents an SOW; is_superuser represents an admin
	'''

	# Phone number is the only field not provided in AbstractUser
	phone = models.CharField(max_length=11, blank=False, null=False)

	# Methods
	# Basic string printing
	def __str__(self):
		return self.get_username() + " (" + self.get_full_name() + ")"

	# Prints all attributes of the user (not covered in tests.py; only used in command line)
	def print_attributes(self):
		print("---\nUsername: " + self.get_username() + "\nFirst name: " + self.first_name + "\nLast name: " + self.last_name + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nActive:" + str(self.is_active) + "\nSuperuser: " + str(self.is_superuser) + "\nStaff: " + str(self.is_staff) + "\n---")

	# Returns if the user is an active staff member (an SOW or an admin)
	def is_active_staff(self):
		return self.is_active and self.is_staff

	# Returns the case load of the user
	def get_case_load(self):
		return CaseLoadUser.objects.filter(user=self)

	# Returns the referrals made by a user
	def get_referrals(self):
		return Referral.objects.filter(user=self)

	# Sets ordering parameters and their ordering priority
	class Meta:
		ordering = ['-is_active', 'is_superuser', 'is_staff', 'username', 'first_name', 'last_name']


# Model for individuals on the case load
class CaseLoadUser(models.Model):
	# Attributes
	first_name = models.CharField(max_length=30, blank=False, null=False)
	last_name = models.CharField(max_length=150, blank=False, null=False)
	nickname = models.CharField(max_length=100, default='')
	email = models.EmailField(max_length=254)
	phone = models.CharField(max_length=11)
	notes = models.CharField(max_length=1000)
	is_active = models.BooleanField(default=True)
	user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)

	# Methods
	# Basic string printing
	def __str__(self):
		return self.get_full_name() + ", phone number " + self.phone

	# Prints the case load user's full name, prettified
	def get_full_name(self):
		return self.first_name + " " + self.last_name

	# Prints all attributes of the case load user (not covered in tests.py; only used in command line)
	def print_attributes(self):
		print("---\nName: " + self.get_full_name() + "\nNickname: " + self.nickname + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nNotes:\n" + self.notes + "\nIs active: " + str(self.is_active) + "\nUser: " + self.user.get_full_name() + "\n---")

	# Grabs all referrals made containing a case load user
	def get_referrals(self):
		return Referral.objects.filter(caseUser=self)

	# Sets ordering parameters and their ordering priority
	class Meta:
		ordering = ['user', 'first_name', 'last_name']


# Model for an entire referral
class Referral(models.Model):
	# Attributes
	email = models.EmailField(max_length=254)
	phone = models.CharField(max_length=11, blank=False, null=False)
	referral_date = models.DateTimeField(default=datetime.now)
	date_accessed = models.DateTimeField(blank=True, null=True)
	notes = models.CharField(max_length=1000)

	# Foreign attributes
	user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
	caseUser = models.ForeignKey(CaseLoadUser, on_delete=models.PROTECT, blank=True, null=True)

	# Methods
	# Sends an email to the referral recipient containing the referred resources
	def sendEmail(self, referralTimeStamp, clientName):
		# Do not send an email if the field is empty
		if (not self.email or self.email == '') and (not self.caseUser or not self.caseUser.email or self.caseUser.email == ''): 
			return 

		# Set the message body containing resource details
		strArgs = [ r.name + ',  ' for r in self.resource_set.all() ]
		strArgs.append('and other resources.')
		resources = [ r for r in self.resource_set.all() ]
		
		# Create username string
		userName = self.user.get_full_name()

		# Create email contents
		subject = 'NewERA412 Referral from {}: {}'.format(userName, ''.join(strArgs))
		html_message = render_to_string('NewEra/referral_mailer.html', {'resources': resources, 'userName': userName, 'notes': self.notes, 'timeStamp': referralTimeStamp, 'clientName': clientName })
		plain_message = strip_tags(html_message)
		from_email = settings.EMAIL_HOST_USER
		
		# Set recipient
		to = self.email
		if to == None or to == '':
			to = self.caseUser.email

		# Send the email
		mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message, fail_silently=True)

	# Sends a text message to the referral recipient containing the referred resources
	def sendSMS(self, smsCarrier, referralTimeStamp, clientName):
		# Do not send a text if the field is empty
		if (not self.phone or self.phone == '') and (not self.caseUser or not self.caseUser.phone or self.caseUser.phone == ''):
			return

		# Create username string and set from_email
		userName = self.user.get_full_name()
		from_email = settings.EMAIL_HOST_USER

		# Set recipient
		to = self.phone
		if to == None or to == '':
			to = self.caseUser.phone
		to = to + SMS_CARRIERS[smsCarrier]

		# Set the message intro string based on whether the referral is to someone on the case load or out of the system
		if (clientName):
			messageIntro = '\n Hi {}, \n {} \n We\'ll send you another text with some links. --{}'.format(clientName, self.notes, userName)
		else:
			messageIntro = '\n {} \n We\'ll send you another text with some links. --{}'.format(self.notes, userName)

		# Send an initial message
		mail.send_mail('NewERA Referral', messageIntro, from_email, [to], fail_silently=False)

		# Create the query string and the message body
		queryString = '?key=' + referralTimeStamp
		links = [ '\n' + r.name + ': https://newera-app.herokuapp.com/resources/' + str(r.id) + queryString + '\n' for r in self.resource_set.all() ]
		messageBody = ''.join(links) + '--- \n See us online for more: newera-app.herokuapp.com'
		
		# Send the actual text message
		mail.send_mail('Links', messageBody, from_email, [to], fail_silently=True)
	
	# Basic string printing
	def __str__(self):
		# name = (first_name == None || last_name == None) ? self.get_full_name() : "(unknown)"
		return "Referral sent to " + self.phone + " by " + self.user.get_full_name() + " on " + self.referral_date.strftime("%m-%d-%Y")

	# Prints all attributes of the referral (not covered in tests.py; only used in command line)
	def print_attributes(self):
		print("---\nReferred by: " + self.user.get_full_name() + "\nReferred to: " + self.caseUser.phone + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nReferral date: " + self.referral_date.strftime("%m-%d-%Y") + "\nDate accessed: " + self.date_accessed.strftime("%m-%d-%Y") + "\nNotes: " + self.notes + "\n---")

	# Sets ordering parameters and their ordering priority
	class Meta:
		ordering = ['referral_date', 'user', 'caseUser']


# Model representing a tag
class Tag(models.Model):
	# Attributes
	name = models.CharField(max_length=30)

	# Methods
	# Basic string printing
	def __str__(self):
		return self.name

	# Prints all attributes of the referral (not covered in tests.py; only used in command line)
	def print_attributes(self):
		print("---\nName: " + self.name + "\n---")

	# Sets ordering parameters and their ordering priority
	class Meta:
		ordering = ['name']


# Model representing one resource as it exists in isolation
class Resource(models.Model):
	# Attributes
	name = models.CharField(max_length=100, blank=False, null=False)
	description = models.CharField(max_length=1000)
	hours = models.CharField(max_length=1000, default='')
	# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
	email = models.EmailField(max_length=254)
	# We can change this later if needed
	phone = models.CharField(max_length=11)
	extension = models.CharField(max_length=11, blank=True, null=True)
	street = models.CharField(max_length=100)
	street_secondary = models.CharField(max_length=100, default='')
	city = models.CharField(max_length=100, default="Pittsburgh")
	# This should account for 5-digit and 10-digit zip codes
	zip_code = models.CharField(max_length=10)
	# Refers to two digits
	state = models.CharField(max_length=2, default="PA")
	image = models.FileField(blank=True)
	content_type = models.CharField(max_length=50, blank=True)
	url = models.URLField()
	clicks = models.IntegerField(default=0)
	is_active = models.BooleanField(default=True)

	contact_name = models.CharField(max_length=181)
	contact_position = models.CharField(max_length=100)
	# Assuming fax number is like a phone number (limited to 10 digits)
	fax_number = models.CharField(max_length=10)
	# This can be the same as or different from the organizational email
	contact_email = models.EmailField(max_length=254)

	# Many-to-many foreign keys
	# Blank section added for the admin dashboard management (otherwise resources can't be added)
	tags = models.ManyToManyField(Tag, blank=True)
	referrals = models.ManyToManyField(Referral, blank=True)

	# Methods
	# Basic string printing
	def __str__(self):
		return self.name

	# Prints all attributes of the resource except image, content_type, tags, and referrals (not covered in tests.py; only used in command line)
	def print_attributes(self):
		print("---\nName: " + self.name + "\nDescription: " + self.description + "\nHours:" + self.hours + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nExtension: " + self.extension  + "\nStreet: " + self.street + "\nSecondary Street: " + self.street_secondary + "\nCity: " + self.city + "\nState: " + self.state + "\nZip code: " + self.zip_code + "\nURL: " + self.url + "\nContact name: " + self.contact_name + "\nContact position: " + self.contact_position + "\nContact email: " + self.contact_email + "\nFax number: " + self.fax_number + "\nClicks: " + str(self.clicks) + "\n---")

	# Sets ordering parameters and their ordering priority
	class Meta:
		ordering = ['name']
