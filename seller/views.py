# pylint: disable=E1101
# pylint: disable=E0401

from datetime import datetime
from django.conf import settings
from django.shortcuts import render,redirect
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from django.core.files.storage import FileSystemStorage
from home.models import User,Product,ProductCategories,Order,OrderItem
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum
import os
# Create your views here.
def index(request):
    if not request.session.get('seller_id'):
        return redirect('/seller/login')
    

    seller_id = request.session.get('seller_id')
    seller = User.objects.get(id=seller_id)
    seller_items = Product.objects.filter(user_id=seller)
    total_sales = sum([item.num_sold for item in seller_items])
    total_revenue = sum([item.get_total_item_price() for item in OrderItem.objects.filter(item__in=seller_items, ordered=True)])
    
    context={
        'url': "seller/home.html",
        'total_sales' : total_sales,
        'product_count': len(seller_items),
        'total_revenue' : total_revenue,
    } 
    return render(request, 'seller/index.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)                
        except User.DoesNotExist:
            error_message = 'Email or password is incorrect.'
            context['error_message'] = error_message
            return render(request,'seller/login.html', context)
        context={}
        if  check_password(password,user.password):
            # Login successful
            if user.user_type != 1  or user.approved == False:
                error_message = 'Sorry,you dont have asscess.'
                context['error_message'] = error_message
                return render(request,'seller/login.html', context)
            
            request.session['seller_id'] = user.id
            request.session['sellername'] = user.first_name
            
            return redirect('/seller/index')
        
        else:
            error_message = 'Email or password is incorrect.'
            context['error_message'] = error_message
            return render(request,'seller/login.html', context)
            
    else:  
        return render(request, 'seller/login.html')

def manage_account(request):
    if not request.session.get('seller_id'):
        return redirect('/seller/login')
    user = User.objects.get(id = request.session.get('seller_id'))
    context={
        'url': "seller/manage_account.html",
        'user': user
    } 
    if request.method == 'POST':
        email = request.POST.get('email')
        phone_number = request.POST.get('contact')
        #checking for if email is already existed or not
        if email != user.email: # Only check for email uniqueness if email is being changed
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                context['message'] = "Email already exists."
                return render(request,"seller/index.html",context)
        
        #checking for if phone number is already existed or not
        if phone_number != user.phone_number: # Only check for email uniqueness if email is being changed
            if User.objects.filter(phone_number=phone_number).exclude(id=user.id).exists():
                context['message'] = "Phone number already exists."
                return render(request,"seller/index.html",context)
            
        user.first_name = request.POST.get('firstname')
        user.last_name = request.POST.get('lastname')
        user.email = email
        user.phone_number = phone_number
        user.save()
        message  = "Profile updated successfully."
        context['message'] = message
    
    return render(request,"seller/index.html",context)

def add_product(request):
    if not request.session.get('seller_id'):
        return redirect('/seller/login')
    context={
        'url': "seller/add_product.html",
        'product_categories': ProductCategories.objects.all()
    } 
    if request.method == 'POST':
        product_name = request.POST.get('name')
        product_type_id = request.POST.get('type')
        description = request.POST.get('description')
        product_price = request.POST.get('amount')
        quantity = request.POST.get('quantity')  
        seller_id = request.session.get('seller_id')
        user = User.objects.get(id=seller_id)
        try:
            product_image = request.FILES['image']
            # Generate a unique filename for the uploaded image
            filename = f"product_{datetime.now().strftime('%Y%m%d%H%M%S')}.{product_image.name.split('.')[-1]}"
            # Save the uploaded image to the media/product directory
            with open(settings.MEDIA_ROOT + '/product/' + filename, 'wb+') as destination:
                for chunk in product_image.chunks():
                    destination.write(chunk)
        except KeyError:
            filename = None
        product_type = ProductCategories.objects.get(id=product_type_id)
        product = Product(product_name=product_name,product_type=product_type,description=description,stock=quantity,amount=product_price,date_added=datetime.today(),user_id=user)
        if filename:
            product.product_image = "product/"+filename
        product.save()
          
    return render(request, 'seller/index.html',context)

def edit_product(request,product_id):
    product = Product.objects.get(id=product_id)
    context={
        'url': "seller/edit_product.html",
        'product': product,
        'product_categories': ProductCategories.objects.all()

    }
    return render(request, 'seller/index.html', context)

def update_product(request):
    if not request.session.get('seller_id'):
        return redirect('/seller/login')
    
    if request.method == 'POST':
        id = request.POST.get('id')
        context={
            'url': "seller/edit_product.html",
            'product_categories': ProductCategories.objects.all(),
            
        } 
        product = Product.objects.get(id=id)
        product.product_name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.amount = request.POST.get('amount') 
        product.stock = request.POST.get('quantity')
        product_type_id = request.POST.get('type')
        product_type = ProductCategories.objects.get(id=product_type_id)
        product.product_type = product_type
        try:
            product_image = request.FILES['image']
            # Generate a unique filename for the uploaded image
            filename = f"product_{datetime.now().strftime('%Y%m%d%H%M%S')}.{product_image.name.split('.')[-1]}"
            # Save the uploaded image to the media/product directory
            with open(settings.MEDIA_ROOT + '/product/' + filename, 'wb+') as destination:
                for chunk in product_image.chunks():
                    destination.write(chunk)

            # delete the old image field
            if product.product_image:
                old_image_path = os.path.join(settings.MEDIA_ROOT, product.product_image.name)
                if os.path.isfile(old_image_path):
                    os.remove(old_image_path)
        except KeyError:
            filename = None
        if filename is not None:
            product.product_image = "product/"+filename
        else:
            product.product_image = product.product_image
        product.save()
        error_message = 'Product Details Updated Successfully.'
        context['message'] = error_message
        context['product'] = Product.objects.get(id=id)
        
    return render(request,'seller/index.html', context)

def delete_product(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        product = Product.objects.get(id=product_id)
        product.delete()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False})
    
def productList(request):
    if not request.session.get('seller_id'):
        return redirect('/seller/login')
    seller_id = request.session.get('seller_id')
    context={
        'url': "seller/product_list.html",
        'products': Product.objects.filter(user_id=seller_id)
    } 
    return render(request,"seller/index.html",context)
    

def logoutUser(request):
    logout(request)
    return redirect("/seller/login")
