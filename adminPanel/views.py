# pylint: disable=E1101
# pylint: disable=E0401
# pylint: disable=C0303
# pylint: disable=C0411
from datetime import datetime
from django.conf import settings
from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password,make_password
from django.contrib import messages
from home.models import *
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import os

# Create your views here.
def index(request):
    if not request.session.get('admin_id'):
        return redirect('/adminPanel/login')
    
    customer = User.objects.filter(user_type=2)
    seller = User.objects.filter(user_type=1)
    product_category = ProductCategories.objects.all()
    products = Product.objects.all()
    order = Order.objects.exclude(date_ordered = None)
    order_items = OrderItem.objects.filter(ordered = True)

    total = 0
    for item in order:
        total += item.get_total()
    context={
        'url': "adminPanel/home.html",
        'customer_count': customer.count,
        'seller_count': seller.count,
        'category_count': product_category.count,
        'product_count': products.count,
        'product_delivery_count': order_items.count,
        'total_revenue': total
    } 

    return render(request, 'adminPanel/index.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        context={}
        try:
            user = User.objects.get(email=email)                
        except User.DoesNotExist:
            context['error_message'] = "Email or Password is incorrect."
            return render(request, 'adminPanel/login.html', context)

        if  check_password(password,user.password):
            if(user.user_type != 0):
                context['error_message'] = "Sorry , You dont have access."
                return render(request, 'adminPanel/login.html', context)
            # Login successful
            request.session['admin_id'] = user.id
            request.session['adminname'] = user.first_name
            return redirect('/adminPanel/index')
        
        else:
            context['error_message'] = "Email or Password is incorrect."
            return render(request, 'adminPanel/login.html', context)
    else:  
        return render(request, 'adminPanel/login.html')

def seller_list(request):
    context={
        'url': "adminPanel/seller_list.html",
        'users': User.objects.filter(user_type=1)
    } 
    return render(request,"adminPanel/index.html",context)

def delete_user(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user = User.objects.get(id=user_id)
        user.delete()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})

def approve_user(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user = User.objects.get(id=user_id)
        user.approved = True
        user.save()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})
    
def restrict_user(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        user = User.objects.get(id=user_id)
        user.approved = False
        user.save()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})
    
def product_category(request):
    if not request.session.get('admin_id'):
        return redirect('/adminPanel/login')
    context={
        'url': "adminPanel/product_type.html",
        'categories': ProductCategories.objects.all()
    } 
    return render(request,"adminPanel/index.html",context)

def add_product_category(request):
    if not request.session.get('admin_id'):
        return redirect('/adminPanel/login')
    context={
        'url': "adminPanel/addProduct.html",
        'product_categories': ProductCategories.objects.all()
    }
    id = request.POST.get('id')
    if id:
        if request.method == 'POST':
            category = ProductCategories.objects.get(id = id)
            category.product_type = request.POST.get('type')
            category.description = request.POST.get('description')
            category.save()
            messages.info(request,"PRODUCT INFORMATION UPDATED SUCCESFULLY")
            
    else: 
        if request.method == 'POST':
            product_type = request.POST.get('type')
            description = request.POST.get('description') 
            product = ProductCategories(product_type=product_type,description=description)
            product.save()
            messages.info(request,"Product Category added successfully")
            # return redirect('/adminPanel/productType')  
    
    return render(request, 'adminPanel/index.html',context)

def edit_category(request,category_id):
    category = ProductCategories.objects.get(id=category_id)
    context={
        'url': "adminPanel/addProduct.html",
        'category': category,
    }

    return render(request, 'adminPanel/index.html', context)

def delete_category(request):
    if request.method == "POST":
        category_id = request.POST.get("category_id")
        category = ProductCategories.objects.get(id=category_id)
        category.delete()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})
    
def contact(request):
    context = {
        'url' : 'adminPanel/messages.html',
        'contacts' : Contact.objects.all()
    }
    return render(request,'adminPanel/index.html',context)

def logoutUser(request):
    logout(request)
    return redirect("/adminPanel/login")
