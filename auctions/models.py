from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
	name = models.CharField(max_length=50, unique=True)

	def __str__(self):
		return self.name

class Listing(models.Model):
	title = models.CharField(max_length=100, unique=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
	currentPrice = models.DecimalField(max_digits=12, decimal_places=2)
	description = models.TextField()
	isActive = models.BooleanField()
	imageUrl = models.URLField()
	category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings")

	# def updatePrice(self):
	# 	bids = self.bids.all()


	def __str__(self):
		return f"{self.title} currently selling at ${self.currentPrice}"

class Bid(models.Model):
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

	def __str__(self):
		return f"bid for {self.listing.title}"

class Comment(models.Model):
	comment = models.TextField()
	commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
	
	def __str__(self):
		return f"{self.commenter.first_name}'s comment"

