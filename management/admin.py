from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(CustomUser) 
admin.site.register(Customer) 
admin.site.register(CustomOrderItem)
admin.site.register(CustomServiceOrderItem)
admin.site.register(CustomOrder)
admin.site.register(Category) 
admin.site.register(Product) 
admin.site.register(ProductPurchased) 