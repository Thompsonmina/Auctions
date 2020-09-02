from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.db import IntegrityError
from django.forms import modelform_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from decimal import *


from .models import *
from .forms import *

def index(request):
    """ render the all the active listings """

    # todo implement
    # create a watchlist for a user if Logged in and the watchlist doesn't yet exist
    if request.user.is_authenticated and "watchlist" not in request.session:
        request.session["watchlist"] = []
    
    return render(request, "auctions/index.html", {"listings": Listing.objects.filter(isActive=True)})

@login_required(login_url="/login")
def create_listing(request):
    # create a listing model form
    if request.method == "POST":

        # validate and save from the formdata to the database
        form = ListingForm(request.POST)
        DEFAULTIMAGEURL = "https://res.cloudinary.com/opuye/image/upload/h_300,c_scale/v1598563707/no-image.png"

        try:
            listing = form.save(commit=False)
            if not listing.imageUrl:
                listing.imageUrl = DEFAULTIMAGEURL

            listing.seller = request.user
            listing.isActive = True
            listing.save()
        except:
            #re-render the form with errors
            return render(request, "auctions/create_listing.html", {"form":form})

        return redirect(reverse("index"))
    else:
        return render(request, "auctions/create_listing.html",{ 
                        "form":ListingForm(initial={"imageUrl":""})})

def categories(request):
    # get all the category names from the database and render
    categories = Category.objects.all().values_list("name", flat=True).order_by("name")
    return render(request, "auctions/categories.html", {"categories":categories})

def category_listings(request, category):
    # get a particular category from the database and get its active listings
    try:
        category = Category.objects.get(name=category)
    except  Category.DoesNotExist:
        return render(request, "auctions/errors.html", {"error_message":f"the url argument {category} is not valid"})

    category_listings = category.listings.filter(isActive=True).values()
    return render(request, "auctions/category_listings.html", {"listings":category_listings})

def single_listing(request, listing):
    # on get display the listing if parameters are valid
    try:
        listing = Listing.objects.get(id=request.GET["id"], title=listing)
    except Listing.DoesNotExist:
         return render(request, "auctions/errors.html", {
            "error_message":"listing does not exist, url arguements might be wrong"
        })
    
    # if the user is logged in and the listing is closed, check if the user is the winner of the bid
    if request.user.is_authenticated and listing.isClosed():
        user_is_winner = listing.highestBidder() == request.user
    else:
        user_is_winner = False


    # create a comment model form to be displayed on the page 
    CommentForm = modelform_factory(Comment, exclude=("commenter","listing"))
    
    return render(request, "auctions/single_listing.html",{
        "listing":listing, "user_is_winner":user_is_winner,
        "commentform":CommentForm,
        "category": listing.category.name 
    })
       
@login_required(login_url="/login")
def make_bid(request, listing_id):
    # create a new bid for a user if the amount she/he submits is valid
    if request.method == "POST":
        bid = request.POST["bid"]

        # create a new decimal and verify that its valid
        getcontext().prec = 12
        try:
            bid = Decimal(bid).quantize(Decimal("0.01"),rounding=ROUND_DOWN)
        except InvalidOperation:
            return render(request, "auctions/errors.html", {
                "error_message":
                "Invalid parameter: the arguement you passed as a bid is not in the correct format"
                })
       # might add test case
        try:
            listing = Listing.objects.get(pk=listing_id)
        except  Listing.DoesNotExist:
            return render(request, "auctions/errors.html", {"error_message":f"error: listing_id not valid"})
        
        # if the bid is valid create a new bid object, save to db and update the listing price
        if listing.isActive and listing.isValidBid(bid):
            Bid.objects.create(amount=bid, listing=listing, owner=request.user)
            return redirect(reverse("single_listing", 
                args=[listing.title]) +f"?id={listing.id}")
            
        # render error if the bid doesn't pass requirements
        return render(request, "auctions/errors.html", {
            "error_message":" your bid is not valid, it's too small"
        }) 

@login_required(login_url="/login")
def close_bid(request, listing_id):
    """ turns a listing inactive, so no more bids can be made""" 
    try:
       listing = Listing.objects.get(pk=listing_id) 
    except  Listing.DoesNotExist:
        return JsonResponse({"success":False})

    if request.user == listing.seller:
        listing.isActive = False
        listing.save()
        return JsonResponse({"success":True})

    return JsonResponse({"success":False})

@login_required
def add_comment(request, listing_id):
    """ get a comment message from the listing page and add it"""
    if request.method == "POST":
        try:
            listing = Listing.objects.get(pk=listing_id)
        except Listing.DoesNotExist:
            return render(request, "auctions/errors.html", {"error_message":
                "something went wrong, the id url argument is not valid"})

        CommentForm = modelform_factory(Comment, exclude=("commenter","listing"))
        # validate and save from the formdata to the database
        form = CommentForm(request.POST)
        try:
            comment = form.save(commit=False)
            comment.commenter = request.user
            comment.listing = listing
            comment.save()
        except:
            # if something went wrong with comment form 
            return render(request, "auctions/errors.html", {"error_message":
                "something went wrong with the submission of your comment, try again"})

        return redirect(reverse("single_listing", 
                args=[listing.title]) +f"?id={listing.id}")

@login_required(login_url="/login")
def watchlist(request):
    # returns the listings in a watchlist 
    listofPks = request.session["watchlist"]
    return render(request, "auctions/watchlist.html", 
        {"listings": Listing.objects.in_bulk(listofPks).values()})

@login_required(login_url="/login")
def add_or_delete_from_watchlist(request):
    #adds or removes a listing id from a user's watchlist

    try: # check if arguments are valid
        listing_id = request.GET["listing_id"]
        action = request.GET["action"]
    except:
        return JsonResponse({"success":False, "error":"invalid argument(s)"})

    # store the listing and clone the session watchlist for modification
    listing = Listing.objects.filter(pk=listing_id,isActive=True)
    watchlist = request.session["watchlist"]

    # add or remove a listing or render an error 
    if action.lower() == "add" and listing:
        if listing[0].id not in watchlist:
            watchlist.append(listing[0].id) 
            request.session["watchlist"] = watchlist

    elif action.lower() == "delete" and listing:
        watchlist.remove(listing[0].id)
        request.session["watchlist"] = watchlist
    else:
        return JsonResponse({"success":False, "error":"invalid argument(s)"})

    return JsonResponse({"success":True})

def in_watchlist(request):
    """ check if a listing is a user's watchlist and returns a json response signifying"""
    try:
        listing_id = int(request.GET["listing_id"])
    except:
        return JsonResponse({"success":False, "error":"invalid argument"})
    if request.user.is_authenticated:
        is_in_watchlist = listing_id in request.session["watchlist"]
        return JsonResponse({"in_watchlist": is_in_watchlist, "success":True}) 
    else:
        return JsonResponse({"success":False, "error":"user not logged in"})

""" Authentication views """
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

