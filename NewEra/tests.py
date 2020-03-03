from django.test import TestCase
from .models import User, CaseLoad, Referral, Resource, Tag, ResourceReferral, ResourceTag

import datetime

# Delete everything
User.objects.all().delete()
CaseLoad.objects.all().delete()
Referral.objects.all().delete()
Resource.objects.all().delete()
Tag.objects.all().delete()
ResourceReferral.objects.all().delete()
ResourceTag.objects.all().delete()

# Set up users
admin = User.objects.create(username="adminguy", password="administrator45", first_name="Admin", last_name="Guy", email="testemail@check.com", phone="5555555556", is_superuser=True)
brenth = User.objects.create(username="bhong", password="testsyay", first_name="Brent", last_name="Hong", is_staff=True)
maxk = User.objects.create(username="mkornyev", password="testtime", first_name="Max", last_name="Kornyev", email="maxk@testingsuite.net", is_staff=True)
joeyp = User.objects.create(username="jperrino", password="testtest", first_name="Joey", last_name="Perrino", is_staff=True, is_active=False)

# Set up case load
c1 = CaseLoad.objects.create(first_name="George", last_name="Test", phone="5555555555", notes="Test Notes Here", user=brenth)
c2 = CaseLoad.objects.create(first_name="Martha", last_name="Test", phone="5555555555", notes="Test Again and Again", user=brenth)
c3 = CaseLoad.objects.create(first_name="Steve", last_name="Test", phone="5555555555", notes="One More", user=maxk)

# Test cases for User model
class UserTests(TestCase):
	'''
	def setUp(self):
		User.objects.create(username="adminguy", password="administrator45", first_name="Admin", last_name="Guy", email="testemail@check.com", phone="5555555556", is_superuser=True)
		User.objects.create(username="bhong", password="testsyay", first_name="Brent", last_name="Hong", is_staff=True)
		User.objects.create(username="mkornyev", password="testtime", first_name="Max", last_name="Kornyev", email="maxk@testingsuite.net")
		User.objects.create(username="jperrino", password="testtest", first_name="Joey", last_name="Perrino", is_staff=True, is_active=False)
	'''

	def test_active_users(self):
		self.assertEqual(admin.is_active, True)
		self.assertEqual(brenth.is_active, True)
		self.assertEqual(maxk.is_active, True)
		# joeyp should be inactive
		self.assertEqual(joeyp.is_active, False)

	def test_active_staff_users(self):
		self.assertEqual(admin.is_active_staff(), False)
		self.assertEqual(brenth.is_active_staff(), True)
		self.assertEqual(maxk.is_active_staff(), True)
		self.assertEqual(joeyp.is_active_staff(), False)

	def test_superuser(self):
		self.assertEqual(admin.is_superuser, True)
		self.assertEqual(maxk.is_superuser, False)

	def test_case_load(self):
		self.assertEqual(len(list(brenth.get_case_load())), 2)
		self.assertEqual(len(list(maxk.get_case_load())), 1)
		self.assertEqual(len(list(joeyp.get_case_load())), 0)

# Test cases for individuals on a case load
class CaseLoadTests(self):

	def test_case_load_individuals(self):
		pass



