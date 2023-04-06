from django.contrib import admin
from .models import User,Product,Seller,ProductCategories,OrderItem,Order,Address,Contact,WishList
# Register your models here.

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Seller)
admin.site.register(ProductCategories)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Address)
admin.site.register(Contact)
admin.site.register(WishList)





