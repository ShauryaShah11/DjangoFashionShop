from django.urls import path
from home import views
from .views import (
    add_to_wishlist,
    remove_from_wishlist,
    add_to_cart,
)
urlpatterns = [

    path("index",views.index,name="index"),
    path("",views.index,name="home"),
    path("manage_account",views.manage_account,name="manage_account"),
    path("login",views.loginUser,name="login"),
    path("logout",views.logoutUser,name="logout"),
    path("register",views.registerUser,name="register"),

    path("contact_us",views.contact,name="contact_us"),

    path("product",views.ProductView,name="product"),
    path("product_details/<int:product_id>/",views.product_details,name="product_details"),

    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path("cart",views.cart,name="cart"),
    path('remove-from-cart/<int:order_item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('add-to-wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path("wishlist",views.wishlist,name="wishlist"),
    path('wishlist/remove/<int:wishlist_item_id>/', remove_from_wishlist, name='remove_wishlist_item'),

    path("checkout",views.checkout,name="checkout"),
    path("order-history",views.order_history,name="order-history"),
    path("order-summary/<int:order_id>/",views.order_summary,name="order-summary"),

    
]

