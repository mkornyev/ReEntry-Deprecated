from django.test import TestCase
from NewEra.models import User, CaseLoad, Referral, Resource, Tag, ResourceReferral, ResourceTag

import datetime

# Delete everything
User.objects.all().delete()
CaseLoad.objects.all().delete()
Referral.objects.all().delete()
Resource.objects.all().delete()
Tag.objects.all().delete()
ResourceReferral.objects.all().delete()
ResourceTag.objects.all().delete()

# Test cases for User model
class UserTests(TestCase):

	def test_printing(self):
		# Delete relevant models
		User.objects.all().delete()

		# Set up users
		admin = User.objects.create_user(username="admin", password="administrator45", first_name="Admin", last_name="Guy", email="testemail@check.com", phone="5555555556", is_superuser=True)
		brenth = User.objects.create_user(username="brenth", password="testsyay", first_name="Brent", last_name="Hong", is_staff=True)
		maxk = User.objects.create_user(username="maxk", password="testtime", first_name="Max", last_name="Kornyev", email="maxk@testingsuite.net", is_staff=True)
		joeyp = User.objects.create_user(username="joeyp", password="testtest", first_name="Joey", last_name="Perrino", is_staff=True, is_active=False)

		self.assertEqual(str(admin), "admin (Admin Guy)")
		self.assertEqual(str(brenth), "brenth (Brent Hong)")
		self.assertEqual(str(maxk), "maxk (Max Kornyev)")
		self.assertEqual(str(joeyp), "joeyp (Joey Perrino)")

	def test_active_users(self):
		# Delete relevant models
		User.objects.all().delete()

		# Set up users
		admin = User.objects.create_user(username="admin", password="administrator45", first_name="Admin", last_name="Guy", email="testemail@check.com", phone="5555555556", is_superuser=True)
		brenth = User.objects.create_user(username="brenth", password="testsyay", first_name="Brent", last_name="Hong", is_staff=True)
		maxk = User.objects.create_user(username="maxk", password="testtime", first_name="Max", last_name="Kornyev", email="maxk@testingsuite.net", is_staff=True)
		joeyp = User.objects.create_user(username="joeyp", password="testtest", first_name="Joey", last_name="Perrino", is_staff=True, is_active=False)

		self.assertEqual(admin.is_active, True)
		self.assertEqual(brenth.is_active, True)
		self.assertEqual(maxk.is_active, True)
		# joeyp should be inactive
		self.assertEqual(joeyp.is_active, False)

	def test_active_staff_users(self):
		# Delete relevant models
		User.objects.all().delete()

		# Set up users
		admin = User.objects.create_user(username="admin", password="administrator45", first_name="Admin", last_name="Guy", email="testemail@check.com", phone="5555555556", is_superuser=True)
		brenth = User.objects.create_user(username="brenth", password="testsyay", first_name="Brent", last_name="Hong", is_staff=True)
		maxk = User.objects.create_user(username="maxk", password="testtime", first_name="Max", last_name="Kornyev", email="maxk@testingsuite.net", is_staff=True)
		joeyp = User.objects.create_user(username="joeyp", password="testtest", first_name="Joey", last_name="Perrino", is_staff=True, is_active=False)

		self.assertEqual(admin.is_active_staff(), False)
		self.assertEqual(brenth.is_active_staff(), True)
		self.assertEqual(maxk.is_active_staff(), True)
		self.assertEqual(joeyp.is_active_staff(), False)

	def test_superuser(self):
		# Delete relevant models
		User.objects.all().delete()

		admin = User.objects.create_user(username="admin", password="administrator45", first_name="Admin", last_name="Guy", email="testemail@check.com", phone="5555555556", is_superuser=True)
		maxk = User.objects.create_user(username="maxk", password="testtime", first_name="Max", last_name="Kornyev", email="maxk@testingsuite.net", is_staff=True)
		
		self.assertEqual(admin.is_superuser, True)
		self.assertEqual(maxk.is_superuser, False)

	def test_case_load(self):
		# Delete relevant models
		User.objects.all().delete()
		CaseLoad.objects.all().delete()

		# Set up users
		admin = User.objects.create_user(username="admin", password="administrator45", first_name="Admin", last_name="Guy", email="testemail@check.com", phone="5555555556", is_superuser=True)
		brenth = User.objects.create_user(username="brenth", password="testsyay", first_name="Brent", last_name="Hong", is_staff=True)
		maxk = User.objects.create_user(username="maxk", password="testtime", first_name="Max", last_name="Kornyev", email="maxk@testingsuite.net", is_staff=True)
		joeyp = User.objects.create_user(username="joeyp", password="testtest", first_name="Joey", last_name="Perrino", is_staff=True, is_active=False)

		# Set up case load
		c1 = CaseLoad.objects.create(first_name="George", last_name="Test", email="test@test.net", phone="5555555555", notes="Test Notes Here", user=brenth)
		c2 = CaseLoad.objects.create(first_name="Martha", last_name="Test", email="testing@site.org", phone="6666666666", notes="Test Again and Again", user=brenth)
		c3 = CaseLoad.objects.create(first_name="Steve", last_name="Test", email="test@abcd.com", phone="7777777777", notes="One More", user=maxk)

		self.assertEqual(c1.user, brenth)
		self.assertEqual(c2.user, brenth)
		self.assertTrue(len(list(CaseLoad.objects.all())) > 0)
		self.assertEqual(len(list(brenth.get_case_load())), 2)
		self.assertEqual(len(list(maxk.get_case_load())), 1)
		self.assertEqual(len(list(joeyp.get_case_load())), 0)

# Test cases for individuals on a case load
class CaseLoadTests(TestCase):

	def test_printing(self):
		# Delete relevant models
		User.objects.all().delete()
		CaseLoad.objects.all().delete()

		# Set up users
		admin = User.objects.create_user(username="admin", password="administrator45", first_name="Admin", last_name="Guy", email="testemail@check.com", phone="5555555556", is_superuser=True)
		brenth = User.objects.create_user(username="brenth", password="testsyay", first_name="Brent", last_name="Hong", is_staff=True)
		maxk = User.objects.create_user(username="maxk", password="testtime", first_name="Max", last_name="Kornyev", email="maxk@testingsuite.net", is_staff=True)
		joeyp = User.objects.create_user(username="joeyp", password="testtest", first_name="Joey", last_name="Perrino", is_staff=True, is_active=False)

		# Set up case load
		c1 = CaseLoad.objects.create(first_name="George", last_name="Test", email="test@test.net", phone="5555555555", notes="Test Notes Here", user=brenth)
		c2 = CaseLoad.objects.create(first_name="Martha", last_name="Test", email="testing@site.org", phone="6666666666", notes="Test Again and Again", user=brenth)
		c3 = CaseLoad.objects.create(first_name="Steve", last_name="Test", email="test@abcd.com", phone="7777777777", notes="One More", user=maxk)

		self.assertEqual(str(c1), "George Test, phone number 5555555555")
		self.assertEqual(str(c2), "Martha Test, phone number 6666666666")
		self.assertEqual(str(c3), "Steve Test, phone number 7777777777")

	def test_full_name(self):
		# Delete relevant models
		User.objects.all().delete()
		CaseLoad.objects.all().delete()

		# Set up users
		admin = User.objects.create_user(username="admin", password="administrator45", first_name="Admin", last_name="Guy", email="testemail@check.com", phone="5555555556", is_superuser=True)
		brenth = User.objects.create_user(username="brenth", password="testsyay", first_name="Brent", last_name="Hong", is_staff=True)
		maxk = User.objects.create_user(username="maxk", password="testtime", first_name="Max", last_name="Kornyev", email="maxk@testingsuite.net", is_staff=True)
		joeyp = User.objects.create_user(username="joeyp", password="testtest", first_name="Joey", last_name="Perrino", is_staff=True, is_active=False)

		# Set up case load
		c1 = CaseLoad.objects.create(first_name="George", last_name="Test", email="test@test.net", phone="5555555555", notes="Test Notes Here", user=brenth)
		c2 = CaseLoad.objects.create(first_name="Martha", last_name="Test", email="testing@site.org", phone="6666666666", notes="Test Again and Again", user=brenth)
		c3 = CaseLoad.objects.create(first_name="Steve", last_name="Test", email="test@abcd.com", phone="7777777777", notes="One More", user=maxk)

		self.assertEqual(c1.get_full_name(), "George Test")
		self.assertEqual(c2.get_full_name(), "Martha Test")
		self.assertEqual(c3.get_full_name(), "Steve Test")

# Test cases for referrals
class ReferralTests(TestCase):

	def test_printing(self):
		# Delete relevant models
		User.objects.all().delete()
		CaseLoad.objects.all().delete()
		Referral.objects.all().delete()

		# Set up users
		maxk = User.objects.create_user(username="maxk", password="testtime", first_name="Max", last_name="Kornyev", email="maxk@testingsuite.net", is_staff=True)
		joeyp = User.objects.create_user(username="joeyp", password="testtest", first_name="Joey", last_name="Perrino", is_staff=True, is_active=False)

		# Set up case load
		c1 = CaseLoad.objects.create(first_name="Steve", last_name="Test", email="test@abcd.com", phone="7777777777", notes="One More", user=maxk)
		c2 = CaseLoad.objects.create(first_name="Martin", last_name="Tester", email="xyz@test.com", phone="2222222222", notes="Try another test", user=maxk)

		# Set up referrals
		r1 = Referral.objects.create(phone="7777777777", notes="check back next week", user=maxk, case=c1)
		r2 = Referral.objects.create(email="test@abcd.com", phone="5656565656", notes="make sure they are still open", user=joeyp)
		r3 = Referral.objects.create(phone="7777777777", notes="keep it up!", user=maxk, case=c1)
		r4 = Referral.objects.create(phone="2222222222", notes="hope this helps", user=maxk, case=c2)

		self.assertEqual(str(r1), "Referral sent to 7777777777 by Max Kornyev on %s" % datetime.datetime.now().strftime("%m-%d-%Y"))
		self.assertEqual(str(r2), "Referral sent to 5656565656 by Joey Perrino on %s" % datetime.datetime.now().strftime("%m-%d-%Y"))
		self.assertEqual(str(r3), "Referral sent to 7777777777 by Max Kornyev on %s" % datetime.datetime.now().strftime("%m-%d-%Y"))
		self.assertEqual(str(r4), "Referral sent to 2222222222 by Max Kornyev on %s" % datetime.datetime.now().strftime("%m-%d-%Y"))

class ResourceTests(TestCase):

	def test_printing(self):
		# Delete relevant models
		Resource.objects.all().delete()

		# Set up resources
		res1 = Resource.objects.create(name="First Test Resource", email="testresource@res.test")
		res2 = Resource.objects.create(name="Second Test Resource", email="testresource2@res.test")

		self.assertEqual(str(res1), "First Test Resource")
		self.assertEqual(str(res2), "Second Test Resource")

class TagTests(TestCase):

	def test_printing(self):
		# Delete relevant models
		Tag.objects.all().delete()

		# Set up tags
		tag1 = Tag.objects.create(name="Housing")
		tag2 = Tag.objects.create(name="Employment")

		self.assertEqual(str(tag1), "Housing")
		self.assertEqual(str(tag2), "Employment")

class ResourceReferralTests(TestCase):

	def test_printing(self):
		# Delete relevant models
		User.objects.all().delete()
		CaseLoad.objects.all().delete()
		ResourceReferral.objects.all().delete()
		Referral.objects.all().delete()
		Resource.objects.all().delete()

		# Set up users
		maxk = User.objects.create_user(username="maxk", password="testtime", first_name="Max", last_name="Kornyev", email="maxk@testingsuite.net", is_staff=True)
		joeyp = User.objects.create_user(username="joeyp", password="testtest", first_name="Joey", last_name="Perrino", is_staff=True, is_active=False)

		# Set up case load
		c1 = CaseLoad.objects.create(first_name="Steve", last_name="Test", email="test@abcd.com", phone="7777777777", notes="One More", user=maxk)

		# Set up referrals
		r1 = Referral.objects.create(phone="7777777777", notes="check back next week", user=maxk, case=c1)
		r2 = Referral.objects.create(email="test@abcd.com", phone="5656565656", notes="make sure they are still open", user=joeyp)

		# Set up resources
		res1 = Resource.objects.create(name="First Test Resource", email="testresource@res.test")
		res2 = Resource.objects.create(name="Second Test Resource", email="testresource2@res.test")

		# Set up referred resources
		resref1 = ResourceReferral.objects.create(referral=r1, resource=res1)
		resref2 = ResourceReferral.objects.create(referral=r1, resource=res2)
		resref3 = ResourceReferral.objects.create(referral=r2, resource=res2)

		self.assertEqual(str(resref1), "First Test Resource referred to 7777777777")
		self.assertEqual(str(resref2), "Second Test Resource referred to 7777777777")
		self.assertEqual(str(resref3), "Second Test Resource referred to 5656565656")

class ResourceTagTests(TestCase):
	
	def test_printing(self):
		# Delete relevant models
		ResourceTag.objects.all().delete()
		Resource.objects.all().delete()
		Tag.objects.all().delete()

		# Set up resources
		res1 = Resource.objects.create(name="First Test Resource", email="testresource@res.test")
		res2 = Resource.objects.create(name="Second Test Resource", email="testresource2@res.test")

		# Set up tags
		tag1 = Tag.objects.create(name="Housing")
		tag2 = Tag.objects.create(name="Employment")

		# Set up tagged resources
		tagres1 = ResourceTag.objects.create(resource=res1, tag=tag1)
		tagres2 = ResourceTag.objects.create(resource=res1, tag=tag2)
		tagres3 = ResourceTag.objects.create(resource=res2, tag=tag1)

		self.assertEqual(str(tagres1), "First Test Resource has tag Housing")
		self.assertEqual(str(tagres2), "First Test Resource has tag Employment")
		self.assertEqual(str(tagres3), "Second Test Resource has tag Housing")

