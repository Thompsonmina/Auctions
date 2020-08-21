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
		cls.joe = User.objects.create_user(username="joe", password="jjmyboy")
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

	def test_listing_method_isValidBid_works(self):
		""" ensure that the isvalidbid method works as expected"""
		self.assertTrue(self.cloak.isValidBid(Decimal(4000)))
		self.assertFalse(self.cloak.isValidBid(Decimal(1290.3)))

	def test_listing_method_highestBidder_works(self):
		""" ensure that the method returns the expected highest bidder"""
		low_amount = Decimal(2100.34).quantize(Decimal("0.01"))
		high_amount = Decimal(1000200.4).quantize(Decimal("0.01"))
		
		bid = Bid.objects.create(amount=low_amount, owner=self.mike, 
			listing=self.cloak
			)
		higher_bid = Bid.objects.create(amount=high_amount, owner=self.joe,
			listing=self.cloak
			)

		self.assertIsInstance(self.cloak.highestBidder(), User)
		self.assertEqual(self.cloak.highestBidder(), self.joe)

	def test_listing_method_highestBidder_return_none(self):
		""" ensure that the method returns none if a listing does not have bids"""

		item = Listing.objects.create(title="invisible_cloak", seller=self.mike, currentPrice=49.90,
					description="this is a description of stuff that happens when stuff happens",
					isActive=True, imageUrl="imageurleggo", category=self.games)
		# no new bids are linked to item
		self.assertIsNone(item.highestBidder())

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

	def test_create_listing_route_fails_onPOST(self):
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
		client = PersistentSessionClient()
		client.force_login(self.user)
		client.session["watchlist"] = []
		client.session.save()
		response = client.get(reverse("show_watchlist"))

		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, template_name="auctions/watchlist.html")

	def test_watchlist_route_returns_user_listings(self):
		""" ensure that the the correct watchlist listings are returned"""
		# using an extended client object in order to be able to manipulate sessions
		client = PersistentSessionClient()
		client.force_login(self.user)

		listings = list(Listing.objects.all().values_list("pk", flat=True))
		client.session["watchlist"] = listings
		client.session.save()
		response = client.get(reverse("show_watchlist"))
		
		# check that the listings returned are the listings in the session
		
		self.assertEqual(len(listings), len(response.context["listings"]))

	def test_watchlist_route_redirects_when_logged_out(self):
		response = self.client.get(reverse("show_watchlist"), follow=True)
		
		self.assertRedirects(response, f"/login?next={reverse('show_watchlist')}")

	def test_add_or_remove_from_watchlist_route_add(self):
		""" ensure that a listing is added to a watchlist """		
		client = PersistentSessionClient()
		client.force_login(self.user)

		client.session["watchlist"] = []
		client.session.save()
		response = client.get(reverse("edit_watchlist"), data={"action":"add", 
			"listing_id":1
			})
		self.assertJSONEqual(str(response.content, encoding="utf8"),
				 {"success":True})

	def test_add_or_remove_from_watchlist_route_failure(self):
		""" ensure that the route fails when given wrong arguements"""
		self.client.force_login(self.user)

		response = self.client.get(reverse("edit_watchlist"), data={})
		self.assertJSONEqual(str(response.content, encoding="utf8"), 
			{"success":False, "error":"invalid argument(s)"})
	
	def test_single_listing_route_displays_with_valid_arguments(self):
		""" ensure that the page displays if the id and listing name passed to
		the url are valid """

		listing = Listing.objects.get(id=1)
		response = self.client.get(reverse("single_listing", args=[listing.title]),
				data={"id":1
			})

		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, template_name="auctions/single_listing.html")
		self.assertEqual(listing, response.context["listing_details"])

	def test_single_listing_route_fails_with_invalid_arguments(self):
		""" ensure that an error page is rendered if wrong arguments are passed """

		listing = "non-existent-name"
		response = self.client.get(reverse("single_listing", args=[listing]), data={"id":2})

		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, template_name="auctions/errors.html")

	def test_single_listing_route_current_is_the_winner(self):
		""" ensure that the route knows if the current user won a bid"""

		self.client.force_login(self.user)

		listing = Listing.objects.get(id=1)
		listing.isActive = False
		listing.save()
		Bid.objects.create(amount="100000", owner=self.user, listing=listing)
		response = self.client.get(reverse("single_listing", args=[listing.title]),
				data={"id":1
			})

		self.assertTrue(response.context["user_is_winner"])

	def test_single_listing_route_current_user_isnt_the_winner(self):
		""" ensure that the route knows if the current user didnt win  a bid"""

		listing = Listing.objects.filter(id=1).values()[0]
		response = self.client.get(reverse("single_listing", args=[listing["title"]]),
				data={"id":1
			})
		self.assertFalse(response.context["user_is_winner"])

	def test_make_bid_route_valid_bid(self):
		""" ensure that a bid object is created if the bid is valid """
		self.client.force_login(self.user)

		listing = Listing.objects.get(pk=1)
		bid = Decimal(5004.34)
		response = self.client.post(reverse("make_bid", args=[listing.id]), data={
			"bid":bid
			})

		self.assertTrue(bid > Bid.objects.get(pk=1).amount)
		self.assertEqual(1, len(listing.bids.all()))

	def test_make_bid_route_redirects_onSuccess(self):

		self.client.force_login(self.user)
		
		listing = Listing.objects.get(pk=1)
		bid = Decimal(10000.45)
		response = self.client.post(reverse("make_bid", args=[listing.id]), data={
			"bid":bid
		})

		self.assertRedirects(response, reverse("single_listing", 
                args=[listing.title]) +f"?id={listing.id}")

	def test_make_bid_route_invalid_bid(self):
		""" ensure that a wrong bid is handled"""
		self.client.force_login(self.user)

		listing = Listing.objects.get(pk=1)
		bid = 1
		response = self.client.post(reverse("make_bid", args=[listing.id]), data={
			"bid":bid
		})

		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, template_name="auctions/errors.html")

	def test_close_bid_route_listing_has_bids(self):
		""" ensure that a listing is closed if has at least on extra bid"""
		self.client.force_login(self.user)

		bid = Bid.objects.create(amount=Decimal(77.00), owner=self.user,
				listing=Listing.objects.get(pk=1)
			)
		response = self.client.get(reverse("close_bid", args=[1]))
		
		self.assertFalse(Listing.objects.get(pk=1).isActive)

	def test_close_bid_route_invalid_listing(self):
		""" ensure that an error page is rendered if the listing id is not valid """
		self.client.force_login(self.user)

		bid = Bid.objects.create(amount=123, owner=self.user, 
			listing=Listing.objects.get(pk=1))

		response = self.client.get(reverse("close_bid", args=[1300]))
		self.assertJSONEqual(str(response.content, encoding="utf8"), 
			{"success":False
		})

	def test_add_comment_route_comment_succesfully_added(self):
		""" ensure that a comment is added to the db on success"""
		self.client.force_login(self.user)
		listing = Listing.objects.get(id=1)

		data = {"comment": "mr user is making a comment on his computer yeah!"}
		response = self.client.post(reverse("add_comment", args=[listing.id]), data=data)

		self.assertEqual(1, len(Comment.objects.all()))
		self.assertEqual(listing.comments.get(id=1), Comment.objects.get(pk=1))

	def test_add_comment_route_comment_redirects_onSucces(self):
		self.client.force_login(self.user)
		listing = Listing.objects.get(id=1)

		data = {"comment": "mr user is making a comment on his computer yeah!"}
		response = self.client.post(reverse("add_comment", args=[listing.id]), data=data)

		self.assertRedirects(response, reverse("single_listing", 
                args=[listing.title]) +f"?id={listing.id}")


	def test_add_comment_route_handles_invalid_formData(self):
		""" ensure that if something goes wrong an error page is rendered"""
		self.client.force_login(self.user)

		data = {}
		response = self.client.post(reverse("add_comment", args=[1]), data=data)

		# ensure that no comment object is created 
		self.assertEqual(0, len(Comment.objects.all()))

		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, template_name="auctions/errors.html")


	def test_add_comment_route_fails_when_url_arguement_isWrong(self):
		""" ensure that a wrong url arguement passed to the route is handled well"""
		self.client.force_login(self.user)

		wrongArguement = 10000
		data={"comment", "information"}
		response = self.client.post(reverse("add_comment", args=[wrongArguement]))

		self.assertEqual(200, response.status_code)
		self.assertTemplateUsed(response, template_name="auctions/errors.html")
