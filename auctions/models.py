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

	DEFAULTIMAGE = "https://www.freeiconspng.com/uploads/no-image-icon-4.png"
	imageUrl = models.URLField("Image Link", default=DEFAULTIMAGE,
	 help_text="enter an optional image link for your listing")

	DEFAULTCATEGORY = "Untagged"
	category = models.ForeignKey(Category, on_delete=models.CASCADE, to_field="name", related_name="listings",
									 default=DEFAULTCATEGORY)

	# def updatePrice(self):
	# 	bids = self.bids.all()
	def __str__(self):
		return f"{self.title} currently selling at ${self.currentPrice}"

class Bid(models.Model):
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
	owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

	def __str__(self):
		return f"bid for {self.listing.title}"

class Comment(models.Model):
	comment = models.TextField()
	commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
	listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
	
	def __str__(self):
		return f"{self.commenter.get_username()}'s comment"

