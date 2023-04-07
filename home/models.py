# pylint: disable=invalid-str-returned
# pylint: disable=E1101
from django.db import models
from django_countries.fields import CountryField
ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    phone_number = models.BigIntegerField(unique=True)
    # 0 = admin, 1= seller, 2= customer
    USER_TYPE_CHOICES = (
        (0, 'Admin'),
        (1, 'Seller'),
        (2, 'Customer'),
    )
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES)
    date_registered = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    objects = models.Manager()
    # pylint: disable=invalid-str-returned
    def __str__(self):
        return self.first_name 

    def username(self):
        return self.first_name+" "+self.last_name

class Seller(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    def __str__(self) :
        return self.company_name


class ProductCategories(models.Model):
    product_type = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    def __str__(self) :
        return self.product_type
    
class Product(models.Model):
    product_name = models.CharField(max_length=50)
    product_type = models.ForeignKey(ProductCategories, on_delete=models.CASCADE,null=True)
    description=models.TextField(blank=True, max_length=300)
    amount=models.FloatField()
    product_image = models.ImageField(upload_to='product/')
    date_added=models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(User,on_delete=models.CASCADE)
    stock = models.IntegerField(default=1)
    num_sold = models.IntegerField(default=0)

    def __str__(self) :
        return self.product_name


class OrderItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.product_name}"

    def get_total_item_price(self):
        return self.quantity * self.item.amount

class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    date_ordered = models.DateTimeField(blank=True, null=True)
    date_shipped = models.DateTimeField(blank=True, null=True)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return self.user.first_name
    
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total
    
    def save(self, *args, **kwargs):
        # update the number of products sold when an order is saved
        if self.date_ordered:
            for order_item in self.items.all():
                order_item.item.num_sold += order_item.quantity
                order_item.item.save()
        super().save(*args, **kwargs)

    
class Address(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    appartment_address = models.CharField(max_length=100)
    zip = models.CharField(max_length=100)
    country = CountryField(multiple=False,null=True)

    def __str__(self):
        return self.user.first_name
    
class Contact(models.Model):
    name = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField(max_length=200)
    
class WishList(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)

    objects = models.Manager()  # Define the objects manager

    def __str__(self):
        return self.user.first_name+" : "+self.product.product_name

