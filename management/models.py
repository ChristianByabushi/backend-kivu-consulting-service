from PIL import Image
from io import BytesIO
from django.core.files import File
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from datetime import datetime
from num2words import num2words


class CustomUser(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to="uploads/avatar/", blank=True)
    REQUIRED_FIELDS = ['first_name', "last_name", "email"]

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=False, null=False)
    slug = models.SlugField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/{self.slug}"


class Supplier(models.Model):
    name = models.CharField(max_length=255, null=False)
    phoneNumber = models.CharField(max_length=30, null=True)
    adresse = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}.{self.id}"


class Customer(models.Model):
    name = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=30, null=True)
    adresse = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}.{self.id}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category, related_name="products", on_delete=models.SET_NULL, null=True
    )
    unit_measurement = models.CharField(max_length=10, null=False)
    slug = models.SlugField()
    description = models.TextField(blank=False, null=False)
    # price = models.DecimalField(max_digits=10, decimal_places=3)
    image = models.ImageField(upload_to="uploads/products/", blank=True)
    thumbnail = models.ImageField(upload_to="uploads/", blank=True, null=True)
    create_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-create_at",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/{self.category.slug}/{self.slug}"

    def get_image(self):
        if self.image:
            return "http://127.0.0.1:8000" + self.image.url

    def get_thumbnail(self):
        if self.thumbnail:
            return "http://127.0.0.1:8000" + self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbanail(self.image)
                # the object thumbnail is saved or updated
                self.save()
                return "http://127.0.0.1:8000" + self.thumbnail.url
            else:
                return ""

    def make_thumbanail(self, image, size=(300, 200)):
        img = Image.open(image)
        img.convert("RGB")
        img.thumbnail(size)

        thumb_io = (
            BytesIO()
        )  # creation of an in-memory stream used to store thumbail image data
        img.save(
            thumb_io, "JPEG", quality=85
        )  # saves the resized image to the thumb_io stream.
        thumbail = File(thumb_io, name=image.name)
        # creates a File object using the thumb_io stream.
        return thumbail


class ProductPurchased(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=3, null=False)
    stock_quantity = models.DecimalField(max_digits=10,
                                         decimal_places=3, null=False)
    supplier = models.ForeignKey(
        Supplier, related_name='productsProvided', on_delete=models.PROTECT, null=True
    )
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ProductPurchased : #{self.id} - {self.product.name}"


class CustomOrder(models.Model):
    customer = models.ForeignKey(
        Customer, models.PROTECT, related_name='order_Purchased'
    ) 
    created_at = models.DateField(auto_now=True)
    order_date = models.DateField(null=False)
    total_amount = models.DecimalField(max_digits=10,
                                       decimal_places=3, null=True)
    deadline = models.IntegerField(default=0)
    typeOrder = models.BooleanField(default=False)
    # When its false it means that the orderitems have quantity field, otherwise itll be concerning the services.

    def formatted_order_date(self):
        return self.order_date.strftime("%A, %B %d, %Y")

    # def get_total_price_text(self):
    #     if self.total_amount == None:
    #         self.total_amount=0
    #     return num2words(self.total_amount, lang='fr')

    def __str__(self):
        return f"Order #{self.id} - {self.customer.name}"

    class Meta:
        ordering = ("-order_date",)


class CustomOrderItem(models.Model):
    customerOrder = models.ForeignKey(
        CustomOrder, models.CASCADE, related_name='order_items'
    )
    productPurchased = models.ForeignKey(ProductPurchased, models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(max_digits=10, decimal_places=3)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"OrderItem#{self.id}--units"

    def get_total_price(self):
        answer = self.unit_price * self.quantity
        return "{:.3f}".format(answer)


class OrderItem(models.Model):
    customerOrder = models.ForeignKey(
        CustomOrder, models.CASCADE, related_name='list_of_order_items')
    product = models.ForeignKey(Product, models.PROTECT)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    unit_price = models.DecimalField(max_digits=10, decimal_places=3)
    description = models.TextField(blank=True, null=True)
    
    def computeSmallTotal(self):
        return round(self.unit_price * self.quantity, 3)

class ServiceOrderItem(models.Model):
    customerOrder = models.ForeignKey(
        CustomOrder, models.CASCADE, related_name='order_service_items'
    )
    category = models.ForeignKey(Category, models.PROTECT)
    total_price = models.DecimalField(max_digits=10, decimal_places=3)
    description = models.TextField(blank=False, null=False)

    def __str__(self):
        return f"OrderServiceItem#{self.id}"


class Payment(models.Model):
    # customerOrder = models.ForeignKey(
    #     CustomOrder, models.CASCADE, related_name='my_orders'
    # )
    purchase_order = models.ForeignKey(CustomOrder, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=3)
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT)

    def __str__(self):
        return f"Payement for order #{self.purchase_order.id}-{self.amount_paid}" 
    
    def formatted_payment_date(self):
       return self.payment_date.strftime("%A, %B %d, %Y")
