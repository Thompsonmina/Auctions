from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Category(models.Model):
	name = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return self.name

class Listing(models.Model):
	title = models.CharField("Listing Title", max_length=100)
	seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
	currentPrice = models.DecimalField("Start price", max_digits=12, decimal_places=2)
	description = models.TextField("Listing Description")
	isActive = models.BooleanField()

	imageUrl = models.URLField("Image Link", 
					help_text="if no value is put a default value will be assigned", 
					blank=True)

	DEFAULTCATEGORY = "Untagged"
	category = models.ForeignKey(Category, on_delete=models.CASCADE, to_field="name", related_name="listings",
									 default=DEFAULTCATEGORY)

	def isClosed(self):
		""" returns true is a listing is closed"""
		return not self.isActive

	def isValidBid(self, newBid):
		""" takes any numerical arguement that can be passed as an arguement
		to decimal as an arguement and returns true if the bid is bigger than 
		existing bids"""

		bid = self.bids.all().aggregate(models.Max("amount"))["amount__max"]
		if bid:
			return newBid > bid
		return newBid >= self.currentPrice

	def highestBidder(self):
		""" returns the owner of the highest bid, or none if listing doesn't exist"""
		highest_bid = self.bids.all().aggregate(models.Max("amount"))["amount__max"]
		try:
			highest_bid = Bid.objects.get(amount=highest_bid)
		except Bid.DoesNotExist:
			return None

		return highest_bid.owner

	def __str__(self):
		return f"{self.title} currently selling at ${self.currentPrice}"

class Bid(models.Model):
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

	def __str__(self):
		return f"bid for {self.listing.title}"

class Comment(models.Model):
	comment = models.TextField("Leave a comment")
	commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
	
	def __str__(self):
		return f"{self.commenter.get_username()}'s comment"

