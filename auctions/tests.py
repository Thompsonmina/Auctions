from django.test import TestCase
from decimal import *


from .models import User, Listing, Bid, Comment, Category

class ModelsTests(TestCase):

	@classmethod
	def setUpClass(cls):
		""" populate the database with some dummy objects to test"""
		super().setUpClass()
		cls.mike = User(username="mike", password="dougyeahboyyes")
		cls.mike.save()

		cls.games = Category(name="games")
		cls.games.save()

		cls.cloak = Listing(title="invisible_cloak", user=cls.mike, currentPrice=49.90,
					description="this is a description of stuff that happens when stuff happens",
					isActive=True, imageUrl="imageurleggo", category=cls.games)
		cls.cloak.save()

		cls.A_COMMENT = "i would love a harry potter cloak"
		cls.comment = Comment(comment=cls.A_COMMENT, 
						commenter=cls.mike, listing=cls.cloak)
		cls.comment.save()

		
		cls.BID_AMOUNT = Decimal(2321.34).quantize(Decimal("0.01"))
		cls.bid = Bid(amount=cls.BID_AMOUNT, listing=cls.cloak, user=cls.mike)
		cls.bid.save()



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




		
