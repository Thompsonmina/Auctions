from django.test import TestCase
from django.urls import reverse
from decimal import *


from .models import User, Listing, Bid, Comment, Category

class ModelTests(TestCase):

	@classmethod
	def setUpClass(cls):
		""" populate the database with some dummy objects to test"""
		super().setUpClass()
		cls.mike = User.objects.create_user(username="mike", password="dougyeahboyyes")
		cls.games = Category.objects.create(name="games")
		cls.cloak = Listing.objects.create(title="invisible_cloak", user=cls.mike, currentPrice=49.90,
					description="this is a description of stuff that happens when stuff happens",
					isActive=True, imageUrl="imageurleggo", category=cls.games)
	
		cls.A_COMMENT = "i would love a harry potter cloak"
		cls.comment = Comment.objects.create(comment=cls.A_COMMENT, 
						commenter=cls.mike, listing=cls.cloak)
		
		cls.BID_AMOUNT = Decimal(2321.34).quantize(Decimal("0.01"))
		cls.bid = Bid.objects.create(amount=cls.BID_AMOUNT, listing=cls.cloak, user=cls.mike)
		
	def test_category_created_well(self):
		""" check that a category is created well"""
		self.assertIsInstance(self.games, Category)
		self.assertEqual("games", Category.objects.get(id=1).name)

	def test_listing_created_well(self):
		""" check that a listing is created well"""
		self.assertIsInstance(self.cloak, Listing)
		self.assertEqual("invisible_cloak", Listing.objects.get(id=1).title)

	def test_bid_created_well(self):
		""" check that a bid is created well"""
		self.assertIsInstance(self.bid, Bid)
		self.assertEqual(self.BID_AMOUNT, Bid.objects.get(id=1).amount)

	def test_comment_created_well(self):
		""" check that a listing is created well"""
		self.assertIsInstance(self.comment, Comment)
		self.assertEqual(self.A_COMMENT, Comment.objects.get(id=1).comment)


class AuthViewsTests(TestCase):
	
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.USERNAME, cls.PASSWORD = "Jacob", "ishallSTRivetoCreateaninsecurepassword12-"
		cls.user = User.objects.create_user(username=cls.USERNAME, password=cls.PASSWORD)

	# login route
	def test_login_route_on_GET(self):
		response = self.client.get(reverse("login"))

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, template_name="/auctions/login.html")

	def test_login_route_user_login_successful(self):
		""" test that a user has successfully been logged in"""
		data = {"username":self.USERNAME, "password":self.PASSWORD}
		response = self.client.post(reverse("login"), data=data, follow=True)

		self.assertRedirects(response, reverse("index"))

	def test_login_route_user_login_failed(self):
		""" test for if a user is not authenticated """
		data = {"username":"randousername", "password":"randopassword"}
		response = self.client.post(reverse("login"), data=data)

		self.assertEqual(response.status_code, 200)

		# ensure that a status message was passed along on login failure
		self.assertIsNotNone(response.context["message"])

	# register route tests	
	def test_register_route_on_GET(self):
		""" test default log in page"""
		response = self.client.get(reverse("register"))

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, template_name="/auctions/register.html")

	def test_register_route_user_created_successfully(self):
		""" test to ensure that a user was created successfuly"""
		newuser, newuserpassword = "James", "password_hehe"
		data = {"username":newuser, "password":newuserpassword, 
					"email":f"{newuser}@test.com", "confirmation":newuserpassword}
		response = self.client.post(reverse("register"), data=data, follow=True)

		# check if there are 2 users in the db, the user and setup and the new user created
		self.assertEqual(2, len(User.objects.all()))

		self.assertRedirects(response, reverse("index"))

	def test_register_route_user_creation_failed(self):
		""" test for when a user creation fails"""

		# putting in a duplicate user to ensure failure
		data = {"username":self.USERNAME, "password":"bleh", "email":"blabla@mail.com",
					 "confirmation":"bleh"}
		response = self.client.post(reverse("register"), data=data)

		self.assertEqual(200, response.status_code)
		self.assertIsNotNone(response.context["message"])


class MainViewsTests(TestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.category = Category.objects.create(name="random")
		cls.user = User.objects.create_user(username="Tims", password="tiktok")

	def test_index_route(self):
		""" test the index view"""
		response = self.client.get(reverse("index"))

		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, template_name="auctions/index.html")

	def test_create_listing_route_onGet(self):
		""" test that the html displays on get"""
		self.client.force_login(self.user)
		response = self.client.get(reverse("create_listing"))

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, template_name="auctions/create_listing.html")

	def test_create_listing_route_listing_successfully_created_onPOST(self):
		""" test that a listing is created successfully """
		self.client.force_login(self.user)
		data = dict(title="invisible_bag", currentPrice=Decimal(49.90).quantize(Decimal("0.01")),
					description="this is a description of stuff that happens when stuff happens",
					isActive=True, imageUrl="https://www.image.com", category=self.category)
	
		response = self.client.post(reverse("create_listing"), data=data, follow=True)
		
		self.assertEqual(1, len(Listing.objects.all()))
		self.assertRedirects(response, reverse("index"))

	def test_create_listing_route_failed_onPOST(self):
		""" test that the route fails as expected"""
		self.client.force_login(self.user)
		
		# bad inputs for the listing to ensure failure
		data = dict(title="invisible_bag",isActive=True, imageUrl="https://www.image.com", category=self.category)
		response = self.client.post(reverse("create_listing"), data=data)
		
		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, template_name="auctions/create_listing.html")

	def test_create_listing_route_redirects_when_loggedout(self):
		response = self.client.get(reverse("create_listing"), follow=True)
		
		self.assertRedirects(response, "/login?next=/create_listing")
