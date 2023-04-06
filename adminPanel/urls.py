from django.urls import path
from adminPanel import views
from home.views import (
    ProductView,
)
from .views import *
urlpatterns = [

    path("",views.index,name="adminPanel/index"),
    path("index",views.index,name="adminPanel/index"),
    path("login",views.login,name="adminPanel/login"),
    path("logout",views.logoutUser,name="adminPanel/logout"),
    path("productType",views.product_category,name="adminPanel/productType"),
    path("sellerList",views.seller_list,name="adminPanel/sellerList"),
    path("delete_user/", delete_user, name="adminPanel/delete_user"),
    path("approve_user/", approve_user, name="adminPanel/approve_user"),
    path("restrict_user/", restrict_user, name="adminPanel/restrict_user"),
    path("addProduct",views.add_product_category,name="adminPanel/addProduct"),
    path("delete_category/",delete_category,name="adminPanel/delete_category"),
    path("edit_category/<int:category_id>/",edit_category,name="adminPanel/edit_category"),
    path("messages",views.contact,name="adminPanel/messages"),



    
]

