from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from importlib import import_module
from decimal import *

from .models import User, Listing, Bid, Comment, Category

class PersistentSessionClient(Client):
	""" utility class to be able use persistent data in test sessions"""
	@property
	def session(self):
		if not hasattr(self, "_persisted_session"):
			engine = import_module(settings.SESSION_ENGINE)
			self._persisted_session = engine.SessionStore("persistent")
		return self._persisted_session

class ModelTests(TestCase):

	@classmethod
	def setUpClass(cls):
		""" populate the database with some dummy objects to test"""
		super().setUpClass()
		cls.mike = User.objects.create_user(username="mike", password="dougyeahboyyes")
		cls.games = Category.objects.create(name="games")
		cls.cloak = Listing.objects.create(title="invisible_cloak", seller=cls.mike, currentPrice=49.90,
					description="this is a description of stuff that happens when stuff happens",
					isActive=True, imageUrl="imageurleggo", category=cls.games)
	
		cls.A_COMMENT = "i would love a harry potter cloak"
		cls.comment = Comment.objects.create(comment=cls.A_COMMENT, 
						commenter=cls.mike, listing=cls.cloak)
		
		cls.BID_AMOUNT = Decimal(2321.34).quantize(Decimal("0.01"))
		cls.bid = Bid.objects.create(amount=cls.BID_AMOUNT, listing=cls.cloak, owner=cls.mike)
		
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
		self.assertTemplateUsed(response, template_name="auctions/login.html")

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
		self.assertTemplateUsed(response, template_name="auctions/register.html")

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
		# dummy listings
		list1 = Listing.objects.create(title="invisible_bag", seller=cls.user, currentPrice=Decimal(49.90).quantize(Decimal("0.01")),
					description="this is a description of stuff that happens when stuff happens",
					isActive=True, imageUrl="https://www.image.com", category=cls.category)
	

		list2 = Listing.objects.create(title="cloak_of_hiding", seller=cls.user, currentPrice=Decimal(49.90).quantize(Decimal("0.01")),
					description="this is a description of stuff that happens when stuff happens",
					isActive=True, imageUrl="https://www.image.com", category=cls.category)
	

	def test_index_route(self):
		""" test the index view"""
		response = self.client.get(reverse("index"))

		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, template_name="auctions/index.html")
		# ensure that the correct listings are sent
		self.assertEqual(len(Listing.objects.all()), len(response.context["listings"]))

	def test_index_route_watchlist_created_when_logged_in(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse("index"))

		# ensure that a watch list was created for the user
		self.assertIn("watchlist", self.client.session)
	
	def test_index_route_watchlist_not_created_when_not_logged_in(self):
		response = self.client.get(reverse("index"))

		# ensure that a watchlist wasnt created as user isn't logged in
		self.assertNotIn("watchlist", self.client.session)

	def test_create_listing_route_onGet(self):
		""" test that the html displays on get"""
		self.client.force_login(self.user)
		response = self.client.get(reverse("create_listing"))

		self.assertEqual(response.status_code, 200)
		self.assertTemplateUsed(response, template_name="auctions/create_listing.html")

	def test_create_listing_route_listing_successfully_created_onPOST(self):
		""" test that a listing is created successfully """
		self.client.force_login(self.user)
		data = dict(title="testobject", currentPrice=Decimal(49.90).quantize(Decimal("0.01")),
					description="this is a description of stuff that happens when stuff happens",
					imageUrl="https://www.image.com", category=self.category)
	
		response = self.client.post(reverse("create_listing"), data=data, follow=True)
		
		self.assertEqual(1, len(Listing.objects.filter(title="testobject")))
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
		
		self.assertRedirects(response, f"/login?next={reverse('create_listing')}")

	def test_categories_route(self):
		""" test to ensure that the categories route works"""
		response = self.client.get(reverse("categories"))

		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, template_name="auctions/categories.html")
		# ensure that all the categories are sent in the response
		self.assertEqual(len(Category.objects.all()), len(response.context["categories"]))

	def test_category_listings_route_valid_category(self):
		""" test for the listings in a single valid category route"""

		# set a valid category
		category = Category.objects.get(pk=1).name
		response = self.client.get(reverse("category_listings", args=[category]))

		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, template_name="auctions/category_listings.html")
		# ensure that the correct listings are sent
		self.assertEqual(2, len(response.context["listings"]))

	def test_category_listing_route_invalid_category(self):
		""" test to ensure that an invalid category to the route results in a 
			error 
		"""
		category = "invalid Category"
		response = self.client.get(reverse("category_listings", args=[category]))

		self.assertEqual(200, response.status_code)
		self.assertIn("error", response.context["error_message"])
		self.assertTemplateUsed(response, template_name="auctions/errors.html")

	def test_watchlist_route_displays(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse("show_watchlist"))

		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, template_name="auctions/watchlist.html")

	def test_watchlist_route_returns_user_listings(self):
		""" ensure that the the correct watchlist listings are returned"""
		client = PersistentSessionClient()
		client.force_login(self.user)

		listings = list(Listing.objects.all().values_list("title", flat=True))
		client.session["watchlist"] = listings
		client.session.save()
		response = client.get(reverse("show_watchlist"))
		
		# check that the listings returned are the listings in the session
		
		self.assertListEqual(listings, response.context["listings"])

	def test_watchlist_route_redirects_when_logged_out(self):
		response = self.client.get(reverse("show_watchlist"), follow=True)
		
		self.assertRedirects(response, f"/login?next={reverse('show_watchlist')}")






