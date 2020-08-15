from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import IntegrityError
from django.forms import modelform_factory
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Category


def index(request):
    """ render the all the active listings """

    # todo implement pagination
    # create a watchlist for a user if Logged in and the watchlist doesn't yet exist
    if request.user.is_authenticated and "watchlist" not in request.session:
        request.session["watchlist"] = []
    
    return render(request, "auctions/index.html", {"listings": Listing.objects.filter(isActive=True).values()})

@login_required(login_url="/login")
def create_listing(request):
    # create a listing model form
    NewListingForm = modelform_factory(Listing, exclude=("seller","isActive"))

    if request.method == "POST":

        # validate and save from the form to the data to the database
        form = NewListingForm(request.POST)
        try:
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.isActive = True
            listing.save()
        except:
            #re-render the form with errors
            return render(request, "auctions/create_listing.html", {"form":form})

        return redirect(reverse("index"))
    else:
        return render(request, "auctions/create_listing.html",{ 
                        "form":NewListingForm()})

def categories(request):
    # get all the category names from the database and render
    categories = Category.objects.all().values_list("name", flat=True).order_by("name")
    return render(request, "auctions/categories.html", {"categories":categories})

def category_listings(request, category):
    # get a particular category from the database and get its active listings
    try:
        category = Category.objects.get(name=category)
    except  Category.DoesNotExist:
        return render(request, "auctions/errors.html", {"error_message":f"error: {category} category not valid"})

    category_listings = category.listings.filter(isActive=True).values_list("title", flat=True)
    return render(request, "auctions/category_listings.html", {"listings":category_listings})

@login_required(login_url="/login")
def watchlist(request):
    return render(request, "auctions/watchlist.html", 
        {"listings":request.session.get("watchlist", None)})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

