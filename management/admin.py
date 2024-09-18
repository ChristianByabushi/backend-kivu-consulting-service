from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User) 
admin.site.register(Customer) 
admin.site.register(CustomOrderItem)
admin.site.register(ServiceOrderItem)
admin.site.register(CustomOrder)
admin.site.register(Category) 
admin.site.register(Product) 
admin.site.register(ProductPurchased) 
admin.site.register(Payment) 