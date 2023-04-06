# pylint: disable=E1101
# pylint: disable=C0411
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime
from .models import *
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth import logout
from django_countries import countries
from django.utils import timezone

# username = shaurya
# password = admin@11
# Create your views here.


def index(request):
    wishlist_items = WishList.objects.filter(
        user=request.session.get('user_id'))
    count = wishlist_items.count()
    context = {}
    if request.session.get('user_id'):
        context['wishlist_items'] = wishlist_items
        context['count'] = count
    return render(request, "index.html", context)

# -------------------------------------------------------------Manage-Profile Section---------------------------------------


def registerUser(request):
    if request.method == "POST":
        firstname = request.POST.get("firstname")
        lastname = request.POST.get("lastname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone_number = request.POST.get("contact")
        user_type = request.POST.get("user_type")

        if user_type == "customer":
            user_type = 2
        else:
            user_type = 1

        hashed_password = make_password(password)
        print(request.POST)
        context = {}
        # checking for if email is already existed or not
        if User.objects.filter(email=email).exists():
            context['error_message'] = "Email already exists."
            return render(request, "register.html", context)

        # checking for if phone number is already existed or not
        if User.objects.filter(phone_number=phone_number).exists():
            context['error_message'] = "Phone number already exists."
            return render(request, "register.html", context)

        user = User(first_name=firstname, last_name=lastname, email=email, password=hashed_password,
                    phone_number=phone_number, date_registered=datetime.today(), user_type=user_type)
        user.save()
        messages.info(request, "Succesfully registered")
        return redirect("/")

    return render(request, "register.html")


def loginUser(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Email or password is incorrect')
            return redirect('login')

        context = {}
        if check_password(password, user.password):
            # Login successful
            if (user.user_type != 2):
                error_message = 'Sorry,you dont have access.'
                context['error_message'] = error_message
                return render(request, 'login.html', context)

            request.session['user_id'] = user.id
            request.session['username'] = user.first_name

            return redirect('/index')
        else:
            error_message = 'Email or password is incorrect.'
            context['error_message'] = error_message
            return render(request, 'login.html', context)

    return render(request, 'login.html')


def manage_account(request):
    if not request.session.get('user_id'):
        return redirect("/login")
    user = User.objects.get(id=request.session.get('user_id'))
    context = {
        'user': user
    }
    if request.method == 'POST':
        email = request.POST.get('email')
        phone_number = request.POST.get('contact')
        # checking for if email is already existed or not
        if email != user.email:  # Only check for email uniqueness if email is being changed
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                context['error_message'] = "Email already exists."
                return render(request, "manage_account.html", context)

        # checking for if phone number is already existed or not
        if phone_number != user.phone_number:  # Only check for email uniqueness if email is being changed
            if User.objects.filter(phone_number=phone_number).exclude(id=user.id).exists():
                context['error_message'] = "Phone number already exists."
                return render(request, "manage_account.html", context)

        user.first_name = request.POST.get('firstname')
        user.last_name = request.POST.get('lastname')
        user.email = email
        user.phone_number = phone_number
        user.save()
        message = "Profile updated successfully."
        context['error_message'] = message
        return render(request, 'manage_account.html', context)

    return render(request, "manage_account.html", context)


def logoutUser(request):
    logout(request)
    return redirect("/login")

# -------------------------------------------------------------Product Section---------------------------------------


def ProductView(request):
    user_id = request.session.get('user_id')
    wishlist_item = WishList.objects.filter(user_id=user_id)

    products = Product.objects.all()

    print(wishlist_item)
    # Get the selected sorting option from the form data
    selected_option = request.GET.get('speed', 'newness')

    # Sort the products based on the selected option
    if selected_option == 'price-low-to-high':
        products = products.order_by('amount')
    elif selected_option == 'price-high-to-low':
        products = products.order_by('-amount')
    else:
        products = products.order_by('-id')
    context = {

        'products': products,
        'wishlist_items': wishlist_item,

    }
    return render(request, "product.html", context)


def product_details(request, product_id):
    product = Product.objects.get(id=product_id)
    context = {
        'product': product,
    }
    return render(request, "product_details.html", context)

# -------------------------------------------------------------Cart Section---------------------------------------


def cart(request):
    if not request.session.get('user_id'):
        return redirect('/login')
    user = request.session.get('user_id')
    order_item = OrderItem.objects.filter(user=user, ordered=False)
    # redirect to empty cart pge if cart is empty
    if(order_item.count() == 0):
        return render(request, 'empty_cart.html')
    total_amount = sum(
        [item.quantity * item.item.amount for item in order_item])
    shipping_charges = calculate_shipping_charges(total_amount)
    context = {
        'order_items': order_item,
        'total_amount': total_amount,
        'shipping_charges': shipping_charges,
        'grand_total': total_amount+shipping_charges
    }
    return render(request, 'cart.html', context)


def add_to_cart(request, product_id):
    if not request.session.get('user_id'):
        return redirect('/login')

    user_id = request.session.get('user_id')
    user = get_object_or_404(User, id=user_id)

    product = get_object_or_404(Product, id=product_id)

    # Check if the user already has an active order
    order, created = Order.objects.get_or_create(user=user, date_shipped=None)

    # Check if the item is already in the order
    order_item, created = OrderItem.objects.get_or_create(
        item=product, ordered=False, user=user)

    if created:
        order_item.quantity = 1
        order_item.save()
        order.items.add(order_item)
    else:
        order_item.quantity += 1
        order_item.save()

    order.save()
    return redirect('/cart')


def remove_from_cart(request, order_item_id):
    if not request.session.get('user_id'):
        return redirect('/login')

    order_item = get_object_or_404(
        OrderItem, id=order_item_id, user=request.session.get('user_id'), ordered=False)

    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.save()
    else:
        order_item.delete()

    # Check if the order is now empty and delete it if it is
    order = Order.objects.filter(user=request.session.get(
        'user_id'), date_shipped=None).first()
    if order and order.items.count() == 0:
        order.delete()

    return redirect("/cart")


def checkout(request):
    if not request.session.get('user_id'):
        return redirect('/login')
    address = Address.objects.filter(
        user=request.session.get('user_id')).first()
    context = {
        'countries': countries,
        'user': address
    }
    if request.method == 'POST':
        appartment_address = request.POST.get('app_address')
        street_address = request.POST.get('street_address')
        zipcode = request.POST.get('zipcode')
        country = request.POST.get('country')
        payment = request.POST.get('payment_method')

        # Get the user and active order
        user = get_object_or_404(User, id=request.session.get('user_id'))

        # Create a new order for the user
        order = Order.objects.get(user=user, date_shipped=None)

        # Update the order with the shipping address and date ordered
        order.shipping_address = Address.objects.create(
            user=user,
            appartment_address=appartment_address,
            street_address=street_address,
            zip=zipcode,
            country=country,
        )
        order.date_ordered = timezone.now()
        order.save()

        # Process the payment
        if payment == 'cash-on-delivery':
            pass  # Do nothing for COD payments
        else:
            pass  # Process online payments

        # Mark the order items as ordered and reduce the product stock
        for order_item in order.items.all():
            product = order_item.item
            product.stock -= order_item.quantity
            product.save()
            order_item.ordered = True
            order_item.save()

        return redirect('/order-history')

    return render(request, 'checkout.html', context)


def order_history(request):
    user = get_object_or_404(User, id=request.session.get('user_id'))
    order = Order.objects.filter(user=user)
    context = {
        'orders': order,
    }
    return render(request, 'order_history.html', context)


def order_summary(request, order_id):
    if not request.session.get('user_id'):
        return redirect('/login')
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.filter(ordered=True)
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'order_summary.html', context)
# -------------------------------------------------------------Wishlist Section---------------------------------------


def wishlist(request):
    if not request.session.get('user_id'):
        return redirect('/login')

    user_id = request.session.get('user_id')
    context = {
        'wishlist_items': WishList.objects.filter(user_id=user_id)
    }
    return render(request, "wishlist.html", context)


def add_to_wishlist(request, product_id):
    if not request.session.get('user_id'):
        return redirect('/login')

    # Retrieve the product from the database using the product_id
    product = get_object_or_404(Product, id=product_id)
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    # Create a new wishlist item for the current user and product
    wishlist_item, created = WishList.objects.get_or_create(
        user=user, product=product)

    # If the wishlist item was already created for this user and product, do nothing
    if not created:
        messages.warning(request, 'This product is already in your wishlist.')

    # Redirect the user back to the product detail page
    return redirect('/product')


def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = WishList.objects.get(id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('/wishlist')

# -------------------------------------------------------------Other Section---------------------------------------


def contact(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        subject = request.POST.get("subject")
        email = request.POST.get("email")
        send_message = request.POST.get("message")
        obj = Contact(name=name, subject=subject,
                      email=email, message=send_message)
        obj.save()
        # messages.success(request,"Message sent successfully")
        return redirect("/contact_us")
    else:
        return render(request, "contact_us.html")


def calculate_shipping_charges(total_amount):
    if total_amount >= 500:
        return 0
    else:
        return 40
