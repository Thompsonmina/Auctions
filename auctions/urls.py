from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category_listings, name="category_listings"),
    path("watchlist", views.watchlist, name="show_watchlist"),
    path("listings/<str:listing>", views.single_listing, name="single_listing"),
    path("edit_watchlist", views.add_or_delete_from_watchlist, name="edit_watchlist"),
    path("make_bid/<int:listing_id>", views.make_bid, name="make_bid"),
    path("close_bid/<int:listing_id>", views.close_bid, name="close_bid"),
    path("add_comment/<int:listing_id>", views.add_comment, name="add_comment")
]
