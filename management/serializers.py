from rest_framework import serializers
from .models import Category, Product
from .models import *
from django.db.models import F, Sum
import math
from django.template.defaultfilters import date as dateformat


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category', 'description', 'create_at',
                  'unit_measurement', 'category_id', 'get_image')
    # category = CategorySerializerForProduct(allow_null=True)
    # this simple line depth =1, will allows that allw relationships in the model
    # displaying  every field related to that model.
        depth = 1

    def create(self, validated_data):
        # Extract the category data from the validated data
        category_data = validated_data.pop('category', None)

        # Create the product instance without the category field
        product = Product.objects.create(**validated_data)

        # If category data is provided, create the category instance and associate it with the product
        if category_data:
            category = Category.objects.create(**category_data)
            product.category = category
            product.save()
        return product


class SupplierSerializerForProduct(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class ProductPurchasedSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    supplier_id = serializers.IntegerField(write_only=True)
    supplier = SupplierSerializerForProduct(read_only=True)

    class Meta:
        model = ProductPurchased
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    # productsProvided = ProductPurchasedSerializer(many=True, read_only=True)
    productsProvided = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = "__all__"

    def get_productsProvided(self, obj):
        products = obj.productsProvided.all()
        distinct_products = {
            prod.product.id: prod for prod in products}.values()
        serialized_products = ProductPurchasedSerializer(
            distinct_products, many=True).data
        return serialized_products


class CustomOrderSerializerStructureCustomer(serializers.ModelSerializer):
    class Meta:
        model = CustomOrder
        fields = "__all__"


class CustomSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = "__all__"

    def get_orders(self, obj):
        orders = obj.order_Purchased.all()
        ordersItems = OrderItem.objects.all()
        ServiceordersItems = ServiceOrderItem.objects.all()
        for eachOrder in orders:
            if eachOrder.typeOrder == False:
                customerTotal = ordersItems.filter(customerOrder=eachOrder).aggregate(
                    answer=Sum(F('quantity')*F('unit_price'))
                )
            else:
                customerTotal = ServiceordersItems.filter(customerOrder=eachOrder).aggregate(
                    answer=Sum('total_price'))
            eachOrder.total_amount = customerTotal['answer']
            eachOrder.save()

        serialized_orders = CustomOrderSerializerStructureCustomer(
            orders, many=True
        ).data
        return serialized_orders


class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ("id", "name", 'description', "slug",
                  "get_absolute_url", "products")


class CustomOrderItemSerializer(serializers.ModelSerializer):
    productPurchased = ProductPurchasedSerializer(read_only=True)
    productPurchased_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CustomOrderItem
        fields = ('id', 'productPurchased', "productPurchased_id", "description",
                  'unit_price', 'quantity',  'get_total_price')


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CustomOrderItem
        fields = ('id', 'product', "product_id", "description",
                  'unit_price', 'quantity',  'get_total_price')


class ServiceOrderItemSerializer(serializers.ModelSerializer):
    # category = CategorySerializer()
    category = CategorySerializer(read_only=True, many=False)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ServiceOrderItem
        fields = ('id', 'category', 'category_id',
                  'total_price', 'description')

        def delete(self, validated_data):
            raise ('try again')


class ServiceOrderSerializer(serializers.ModelSerializer):
    # Use 'order_items' instead of 'items'
    order_service_items = ServiceOrderItemSerializer(many=True)
    customer = CustomSerializer(read_only=True, many=False)
    customer_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CustomOrder
        fields = ('id', 'customer', "customer_id", 'total_amount', 'order_date', 'typeOrder', 'formatted_order_date',
                  'order_service_items', 'deadline')

    def create(self, validated_data):
        order_items_data = validated_data.pop(
            "order_service_items")  # Use 'order_service_items' here as well
        total_amount = 0
        for item in order_items_data:
            if float(item.get('total_price')) > 0:
                total_amount += float(item.get('total_price'))
            else:
                raise ("The amount of each orderitem must be more than 1 dollar")

        order = CustomOrder.objects.create(
            **validated_data, total_amount=total_amount, typeOrder=True)

        for order_item in order_items_data:
            ServiceOrderItem.objects.create(
                customerOrder=order, **order_item)
        return order


class OrderSerializer(serializers.ModelSerializer):
    # Use 'order_service_items' instead of 'items'
    list_of_order_items = OrderItemSerializer(many=True)
    customer = CustomSerializer()

    class Meta:
        model = CustomOrder
        fields = ('id', 'customer', 'order_date', 'formatted_order_date',
                  'list_of_order_items', 'total_amount', 'deadline', 'typeOrder')

    def get_total_amount(self, obj):
        ordersItems = OrderItem.objects.filter(customerOrder=obj)
        customerTotal = ordersItems.aggregate(
            answer=Sum(F('quantity') * F('unit_price'))
        )
        return customerTotal['answer'] or 0  # Return 0 if answer is None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        total_amount = self.get_total_amount(instance)
        representation['total_amount'] = total_amount
        return representation

    def create(self, validated_data):
        order_items_data = validated_data.pop(
            "list_of_order_items")  # Use 'order_items' here as well
        order = CustomOrder.objects.create(**validated_data)
        for order_item in order_items_data:
            OrderItem.objects.create(customerOrder=order, **order_item)
        return order

# This function contains the productPurchased instead


class CustomOrderSerializer(serializers.ModelSerializer):
    # Use 'order_service_items' instead of 'items'
    order_items = CustomOrderItemSerializer(many=True)
    customer = CustomSerializer()

    class Meta:
        model = CustomOrder
        fields = ('id', 'customer', 'order_date', 'formatted_order_date',
                  'order_items', 'total_amount', 'deadline', 'typeOrder')

    def get_total_amount(self, obj):
        ordersItems = CustomOrderItem.objects.filter(customerOrder=obj)
        customerTotal = ordersItems.aggregate(
            answer=Sum(F('quantity') * F('unit_price'))
        )
        return customerTotal['answer'] or 0  # Return 0 if answer is None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        total_amount = self.get_total_amount(instance)
        representation['total_amount'] = total_amount
        return representation

    def create(self, validated_data):
        order_items_data = validated_data.pop(
            "order_items")  # Use 'order_items' here as well

        order = CustomOrder.objects.create(**validated_data)

        for order_item in order_items_data:
            CustomOrderItem.objects.create(
                customerOrder=order, **order_item, typeOrder=False)
        return order

    # def update(self, instance, validated_data):
    #     order_items_data = validated_data.pop("order_items", None)
    #     print(order_items_data)
    #     try:
    #         if order_items_data is not None:
    #             order_items = instance.order_items.all()
    #             for order_item_data in order_items_data:
    #                 order_item_id = order_item_data.get("id")
    #                 if order_item_id is not None:
    #                     try:
    #                         order_item = order_items.get(pk=order_item_id)
    #                         order_item.quantity = order_item_data.get(
    #                             "quantity", order_item.quantity)
    #                         order_item.unit_price = order_item_data.get(
    #                             "unit_price", order_item.unit_price)
    #                         order_item.save()
    #                     except CustomOrderItem.DoesNotExist:
    #                         # Handle the case where the order item does not exist
    #                         pass
    #         for attr, value in validated_data.items():
    #             setattr(instance, attr, value)
    #         instance.save()
    #     except Exception as e:
    #         # Print the exception and any relevant data
    #         print("Error:", e)
    #         print("Order Items Data:", order_items_data)
    #         print("Instance:", instance)
    #         raise e  # Re-raise the exception after printing
    #     return instance


class PaymentOrderSerializer(serializers.ModelSerializer):
    purchase_order_id = serializers.IntegerField(write_only=True)
    purchase_order = ServiceOrderSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = ('purchase_order_id', 'purchase_order',
                  'payment_date', 'amount_paid')
