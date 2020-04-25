from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate
from django.db import models
from django import forms
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from datetime import datetime

SMS_CARRIERS = {
	'AT&T':    '@txt.att.net',
	'TMobile':' @tmomail.net',
	'Verizon':  '@vtext.com',
	'Sprint':   '@page.nextel.com'
}


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

	phone = models.CharField(max_length=11, blank=False, null=False)

	# We have is_staff and is_superuser, so we don't need to create custom roles

	# Methods
	def __str__(self):
		return self.get_username() + " (" + self.get_full_name() + ")"

	def print_attributes(self):
		print("---\nUsername: " + self.get_username() + "\nFirst name: " + self.first_name + "\nLast name: " + self.last_name + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nActive:" + str(self.is_active) + "\nSuperuser: " + str(self.is_superuser) + "\nStaff: " + str(self.is_staff) + "\n---")

	def is_active_staff(self):
		return self.is_active and self.is_staff

	def get_case_load(self):
		return CaseLoadUser.objects.filter(user=self)

	def get_referrals(self):
		return Referral.objects.filter(user=self)

	class Meta:
		ordering = ['-is_active', 'is_superuser', 'is_staff', 'username', 'first_name', 'last_name']

# Model for individuals on the case load
class CaseLoadUser(models.Model):
	# Attributes
	first_name = models.CharField(max_length=30, blank=False, null=False)
	last_name = models.CharField(max_length=150, blank=False, null=False)
	nickname = models.CharField(max_length=100, default='')
	# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
	email = models.EmailField(max_length=254)
	phone = models.CharField(max_length=11)
	notes = models.CharField(max_length=1000)
	is_active = models.BooleanField(default=True)
	user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)

	# Methods
	def __str__(self):
		return self.get_full_name() + ", phone number " + self.phone

	def get_full_name(self):
		return self.first_name + " " + self.last_name

	def print_attributes(self):
		print("---\nName: " + self.get_full_name() + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nNotes:\n" + self.notes + "\nIs active: " + self.is_active + "\nUser: " + self.user.get_full_name() + "\n---")

	def get_referrals(self):
		return Referral.objects.filter(caseUser=self)

	class Meta:
		ordering = ['user', 'first_name', 'last_name']

# Model for an entire referral
class Referral(models.Model):
	# Attributes
	# https://stackoverflow.com/questions/386294/what-is-the-maximum-length-of-a-valid-email-address
	email = models.EmailField(max_length=254)
	# 10 is the max length to force a phone number to be just the digits
	# We can change this later if needed
	phone = models.CharField(max_length=11, blank=False, null=False)
	referral_date = models.DateTimeField(default=datetime.now)
	# resource_accessed = models.BooleanField()
	date_accessed = models.DateTimeField(blank=True, null=True)
	notes = models.CharField(max_length=1000)

	# Foreign attributes
	user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
	caseUser = models.ForeignKey(CaseLoadUser, on_delete=models.PROTECT, blank=True, null=True)

	# Methods
	def sendEmail(self, referralTimeStamp, clientName):
		if (not self.email or self.email == '') and (not self.caseUser or not self.caseUser.email or self.caseUser.email == ''): 
			return 

		strArgs = [ r.name + ',  ' for r in self.resource_set.all() ]
		strArgs.append('and other resources.')
		resources = [ r for r in self.resource_set.all() ]
		
		userName = self.user.first_name + ' ' + self.user.last_name

		subject = 'NewERA412 Referral from {}: {}'.format(userName, ''.join(strArgs))
		html_message = render_to_string('NewEra/referral_mailer.html', {'resources': resources, 'userName': userName, 'notes': self.notes, 'timeStamp': referralTimeStamp, 'clientName': clientName })
		plain_message = strip_tags(html_message)
		from_email = settings.EMAIL_HOST_USER
		
		to = self.email
		if to == None or to == '':
			to = self.caseUser.email

		mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message, fail_silently=True)

	def sendSMS(self, smsCarrier, referralTimeStamp, clientName): 
		if (not self.phone or self.phone == '') and (not self.caseUser or not self.caseUser.phone or self.caseUser.phone == ''):
			return

		userName = self.user.first_name + ' ' + self.user.last_name
		from_email = settings.EMAIL_HOST_USER
		to = self.phone

		if to == None or to == '':
			to = self.caseUser.phone
		to = to + SMS_CARRIERS[smsCarrier]

		if (clientName):
			messageIntro = '\n Hi {}, \n {} \n We\'ll send you another text with some links. --{}'.format(clientName, self.notes, userName)
		else:
			messageIntro = '\n {} \n We\'ll send you another text with some links. --{}'.format(self.notes, userName)
		mail.send_mail('NewERA Referral', messageIntro, from_email, [to], fail_silently=False)

		queryString = '?key=' + referralTimeStamp
		links = [ '\n' + r.name + ': https://newera-app.herokuapp.com/resources/' + str(r.id) + queryString + '\n' for r in self.resource_set.all() ]
		messageBody = ''.join(links) + '--- \n See us online for more: newera-app.herokuapp.com'
		mail.send_mail('Links', messageBody, from_email, [to], fail_silently=True)
		
	def __str__(self):
		# name = (first_name == None || last_name == None) ? self.get_full_name() : "(unknown)"
		return "Referral sent to " + self.phone + " by " + self.user.get_full_name() + " on " + self.referral_date.strftime("%m-%d-%Y")

	def print_attributes(self):
		print("---\nReferred by: " + self.user.get_full_name() + "\nReferred to: " + self.caseUser.phone + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nReferral date: " + self.referral_date.strftime("%m-%d-%Y") + "\nDate accessed: " + self.date_accessed.strftime("%m-%d-%Y") + "\nNotes: " + self.notes + "\n---")

	class Meta:
		ordering = ['referral_date', 'user', 'caseUser']

# Model representing a tag
class Tag(models.Model):
	# Attributes
	name = models.CharField(max_length=30)

	# Methods
	def __str__(self):
		return self.name

	def print_attributes(self):
		print("---\nName: " + self.name + "\n---")

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
	# Assuming fax number is like a phone number
	fax_number = models.CharField(max_length=10)
	# This may or may not be different from the organizational email
	contact_email = models.EmailField(max_length=254)

	# Many-to-many foreign keys
	# Blank section added for the admin dashboard management (otherwise resources can't be added)
	tags = models.ManyToManyField(Tag, blank=True)
	referrals = models.ManyToManyField(Referral, blank=True)

	# Methods
	def __str__(self):
		return self.name

	def print_attributes(self):
		print("---\nName: " + self.name + "\nDescription: " + self.description + "\nHours:" + self.hours + "\nEmail: " + self.email + "\nPhone: " + self.phone + "\nStreet: " + self.street + "\nZip code: " + self.zip_code + "\nState: " + self.state + "\nURL: " + self.url + "\nClicks: " + str(self.clicks) + "\n---")

	class Meta:
		ordering = ['name']
