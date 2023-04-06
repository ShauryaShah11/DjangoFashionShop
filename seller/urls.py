from django.urls import path
from seller import views
from home.views import (
    ProductView,
)
from .views import *
urlpatterns = [

    path("",views.index,name="seller/index"),
    path("index",views.index,name="seller/index"),
    path("login",views.login,name="seller/login"),
    path("manage_account",views.manage_account,name="seller/manage_account"),
    path("addProduct",views.add_product,name="seller/addProduct"),
    path("updateProduct",views.update_product,name="seller/updateProduct"),
    path("logout",views.logoutUser,name="seller/logout"),
    path("productList",views.productList,name="seller/productList"),
    path("edit_product/<int:product_id>/",edit_product,name="seller/edit_product"),
    path("delete_product/",delete_product,name="seller/delete_product"),


    
]

