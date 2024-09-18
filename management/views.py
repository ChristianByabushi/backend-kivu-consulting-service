from datetime import datetime as datetimeconverter
from datetime import date
from .serializers import ProductPurchasedSerializer
from django.core.paginator import Paginator
from rest_framework.permissions import IsAdminUser
from rest_framework import status
import django_filters
from .models import ProductPurchased
from django.test import TestCase
from django.test import Client
import json
from django.http import HttpResponse
from django.shortcuts import render
import locale
from django.db.models import Sum, Avg, Count, Max, Min
from django.conf import settings
from django.db.models import Q
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone
from django.db.models import FloatField
from django.template.loader import get_template
from django.template import Context
from django.shortcuts import get_object_or_404
from num2words import num2words
# from weasyprint import HTML
from django.db import transaction
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, viewsets, authentication, permissions, status
from rest_framework.viewsets import ModelViewSet
from .models import *

from .serializers import *
from django.http import Http404
from django.db.models import F, ExpressionWrapper, DecimalField
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django_filters import rest_framework as filters
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from django_filters import rest_framework as filters
# Create your views here.

import os


class ClassPagination:
    @staticmethod
    def customize(perpage, page, itemsObject):
        paginator = Paginator(itemsObject, per_page=perpage)
        try:
            itemsObject = paginator.page(number=page)
            return itemsObject
        except EmptyPage:
            return []


class DateUtils(TestCase):
    @staticmethod
    def get_week_date(date):
        start_date = date - timedelta(days=date.weekday())
        end_date = start_date + timedelta(days=6)
        return start_date, end_date

    @staticmethod
    def get_month_date(date):
        # this code add intelligently 32 days to the current date  and obtain the last day of the next month,
        # then replace the day of that month by 1 and susbstract the result by one in order to obtain the last day
        # of the selected day the month
        first_date_of_month = date.replace(day=1)
        last_day_of_month = (date + timedelta(days=32)
                             ).replace(day=1) - timedelta(days=1)
        return first_date_of_month, last_day_of_month

    @staticmethod
    def handleObjectDate(objects, value_date_received, datefield, to_date_measure):
        selected_date = datetime.strptime(
            value_date_received, "%Y-%m-%d").date()
        if to_date_measure == "Week":
            start_date, end_date = DateUtils.get_week_date(selected_date)
            query_filter = (
                Q(**{f"{datefield}__gte": start_date}) &
                Q(**{f"{datefield}__lte": end_date})
            )

            objects = objects.filter(query_filter)
        elif to_date_measure == "Month":
            first_date_of_month, last_day_of_month = DateUtils.get_month_date(
                selected_date)

            query_filter = (
                Q(**{f"{datefield}__gte": first_date_of_month}) &
                Q(**{f"{datefield}__lte": last_day_of_month})
            )
            objects = objects.filter(query_filter)

        elif to_date_measure == "Year":
            year = datetime.strptime(value_date_received, "%Y-%m-%d").year
            query_filter = (
                Q(**{f"{datefield}__year": year})
            )

            objects = objects.filter(query_filter)

        elif to_date_measure == "Day":
            query_filter = (
                Q(**{f"{datefield}__day": selected_date.day}) &
                Q(**{f"{datefield}__year": selected_date.year}) &
                Q(**{f"{datefield}__month": selected_date.month})
            )
            objects = objects.filter(query_filter)
        else:
            query_filter = (
                Q(**{f"{datefield}__day": selected_date.day}) &
                Q(**{f"{datefield}__year": selected_date.year}) &
                Q(**{f"{datefield}__month": selected_date.month})
            )
            objects = objects.filter(query_filter)
        return objects


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('name', 'category', 'category__name', 'create_at')
    ordering_fields = ['name', "description"]
    pagination_class = CustomPageNumberPagination
    # permission_classes = [IsAdminUser]


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all().order_by('-created_at')
    serializer_class = SupplierSerializer
    # filter_backends = (filters.DjangoFilterBackend,)
    # filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminUser]


class ProductPurchasedAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        queryset = ProductPurchased.objects.select_related(
            'supplier', 'product').all().order_by('-created_at')
        datefrom = request.query_params.get('datefrom')
        dateto = request.query_params.get('dateto')
        perpage = request.query_params.get('perpage', 5)
        page = request.query_params.get('page', 1)
        selectedProduct = request.query_params.get('selectedProduct')

        if selectedProduct:
            queryset = queryset.filter(product__id=selectedProduct)
        if datefrom:
            queryset = queryset.filter(created_at__gte=datefrom)
        if dateto:
            queryset = queryset.filter(created_at__lte=dateto)

        # Apply pagination
        paginator = Paginator(queryset, perpage)
        page_obj = paginator.get_page(page)

        serializer = ProductPurchasedSerializer(page_obj, many=True)
        return Response({
            'count': paginator.count,
            'results': serializer.data
        })

    def post(self, request, *args, **kwargs):
        serializer = ProductPurchasedSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            product_purchased = ProductPurchased.objects.get(id=pk)
            product_purchased.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductPurchased.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PaymentsOrderAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None, format=None):
        orderDateFrom = request.query_params.get('orderDateFrom')
        orderDateTo = request.query_params.get('orderDateTo')
        client_id = request.query_params.get('client_id')
        perpage = request.query_params.get('perpage', default=5)
        page = request.query_params.get('page', default=1)

        if int(perpage) < 1:
            perpage = 1

        # Filter order clients based on query parameters
        orderClients = CustomOrder.objects.select_related('customer').prefetch_related(
            'payment_set')  # Pre-fetch related data
        if orderDateFrom:
            orderClients = orderClients.filter(order_date__gte=orderDateFrom)
        if orderDateTo:
            orderClients = orderClients.filter(order_date__lte=orderDateTo)
        if client_id:
            orderClients = orderClients.filter(customer__id=client_id)

        orderPayments = []
        for orderClient in orderClients:
            orderPayment = orderClient.payment_set.aggregate(
                payed_amount=Sum('amount_paid', output_field=FloatField()))
            payments_data = PaymentOrderSerializer(
                orderClient.payment_set, many=True).data  # Serialize payments in bulk

            if not orderPayment['payed_amount']:
                orderPayment['payed_amount'] = 0

            if orderClient.typeOrder == False:
                orderPayments.append(
                    {'paidAmountOrder': orderPayment['payed_amount'],
                     'PayementsOfClient': payments_data,
                     'orderPayment': OrderSerializer(orderClient).data})
            else:
                orderPayments.append(
                    {'paidAmountOrder': orderPayment['payed_amount'],
                     'PayementsOfClient': payments_data,
                     'orderPayment': ServiceOrderSerializer(orderClient).data})
        count = len(orderPayments)
        paginator = Paginator(orderPayments, perpage)
        if int(page) > paginator.num_pages:
            page = paginator.num_pages
        page_obj = paginator.get_page(page)
        orderPayments = list(page_obj)

        context = {
            "count": count,
            "orders": orderPayments
        }

        return Response(context, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = PaymentOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({"message": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PaymentOrderSerializer(payment, data=request.data)
        if serializer.is_valid():
            # Assuming i want to update the user information as well
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        try:
            payment = Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({"message": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def payment_analysis(request):
    orders = CustomOrder.objects.select_related(
        'customer').all()
    totypeOrder = request.query_params.get('typeOrder')
    to_order_date = request.query_params.get('order_date')
    to_date_measure = request.query_params.get('date_measure')
    to_customer = request.query_params.get('customer')
    perpage = request.query_params.get('perpage', default=5)
    page = request.query_params.get('page', default=1)

    if to_customer:
        orders = orders.filter(customer__id=to_customer)
    if totypeOrder:
        if totypeOrder == True:
            orders = orders.filter(typeOrder=True)
        else:
            orders = orders.filter(totypeOrder=False)
    if to_order_date:
        orders = DateUtils.handleObjectDate(
            orders, to_order_date, "order_date", to_date_measure)

    count = len(orders)
    orders = ClassPagination.customize(perpage, page, orders)

    # I groupby, annotate the orders found and summ the amount_paid
    result = []
    for order in orders:
        resultPayment = Payment.objects.filter(
            purchase_order__id=order.id).aggregate(amount_paid_computed=Sum('amount_paid'),
                                                   countTimes=Count('id'))
        if resultPayment['amount_paid_computed'] is None:
            resultPayment['amount_paid_computed'] = 0

        result.append({
            "order": ServiceOrderSerializer(order).data,
            "total_paid": resultPayment,
        })
    return Response({"result": result, "count": count}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def staticanalysis(request):

    return 0


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def get_order_state(request, order_id):
    # Load the HTML template
    template = get_template('reports/order.html')
    # Construct the base URL for static files
    base_url = request.build_absolute_uri(settings.STATIC_URL)
    to_date_measure = request.query_params.get('date_measure')
    customer_id = request.query_params.get('customer_id')
    to_order_date = request.query_params.get('order_date')
    typeOrder = request.query_params.get('typeOrder')
    # Consider only orders which are pratically of store's type
    if customer_id:
        orders = orders.filter(customer__id=customer_id)
    if to_order_date:
        orders = DateUtils.handleObjectDate(
            orders, to_order_date, "order_date", to_date_measure)
    if typeOrder == 'False':
        order = CustomOrder.objects.filter(typeOrder=False).get(id=order_id)
        # Collect all items linked to that order.
        orderItems = OrderItem.objects.filter(customerOrder__id=order_id)
        # All costs of the order
        totalCost = round(
            sum([item.unit_price * item.quantity for item in orderItems]), 3)
        context = {'order': order,
                   'orderItems': orderItems,
                   'totalCost': totalCost,
                   'totalCostInWords': num2words(totalCost, lang='fr'),
                   'base_url': base_url, 'typeOrder': False}
        html_content = template.render(context)
    else:
        order = CustomOrder.objects.filter(typeOrder=True).get(id=order_id)
        serviceOrderItems = ServiceOrderItem.objects.filter(
            customerOrder__id=order_id)
        totalCost = round(
            sum([item.total_price for item in serviceOrderItems]), 3)
        context = {'order': order,
                   'serviceOrderItems': serviceOrderItems,
                   'totalCost': totalCost,
                   'totalCostInWords': num2words(totalCost, lang='fr'),
                   'base_url': base_url, 'typeOrder': True}
        html_content = template.render(context)

    # Generate PDF using WeasyPrint
    pdf_file = HTML(string=html_content, base_url=base_url).write_pdf()

    # Create and return the PDF response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'

    return response

def get_month_name(month_number):
  """
  Returns the full month name for a given integer (1-12).
  """
  if 1 <= month_number <= 12:
    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    return month_names[month_number - 1]
  else:
    raise ValueError("Invalid month number. Please provide a number between 1 and 12.")


@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def dashboardresults(request):
    periodfilter = request.query_params.get('periodfilter')
    filterDate = request.query_params.get('filterDate')
    # Arranged according to the today's date
    orderClients = CustomOrder.objects.all()
    todaySdate = date.today().strftime("%Y-%m-%d") 
    print(filterDate)
    if periodfilter == 'Week':
        orderClients = DateUtils.handleObjectDate(
            orderClients, filterDate, 'order_date', periodfilter)
    elif periodfilter == 'Month':
        orderClients = DateUtils.handleObjectDate(
            orderClients, filterDate, 'order_date', periodfilter)
    elif periodfilter == 'Year':
        orderClients = DateUtils.handleObjectDate(
            orderClients, todaySdate, 'order_date', periodfilter)
    else:
        orderClients = DateUtils.handleObjectDate(
            orderClients, filterDate, 'order_date', "Day")
    totalOrderPayments = 0
    costOfCostOrders = 0
    for orderClient in orderClients:
        costPaymentOrder = Payment.objects.filter(purchase_order=orderClient).aggregate(
            answer=Sum('amount_paid')
        )
        if not costPaymentOrder['answer']:
            costPaymentOrder['answer'] = 0
        totalOrderPayments += costPaymentOrder['answer']
        if orderClient.typeOrder == False:
            costOrder = OrderItem.objects.filter(customerOrder=orderClient).aggregate(
                answer=Sum(F('quantity') * F('unit_price')))
        else:
            costOrder = ServiceOrderItem.objects.filter(customerOrder=orderClient).aggregate(
                answer=Sum('total_price')
            )
        if not costOrder['answer']:
            costOrder['answer'] = 0
        costOfCostOrders += costOrder['answer']

    productsPurchased = ProductPurchased.objects.all()

    products = Product.objects.all()

    storestateItems = []

    for product in products:
        # analyze the purchasement
        # we cheak how many fields have already been sold
        productPurchased = productsPurchased.filter(
            product__id=product.id
        ).aggregate(quantityAlreadyPurchased=Sum('stock_quantity'),
                    countTimesPurchased=Count('id'),

                    averageUnitPrice=Sum(
            F('unit_price') * F('stock_quantity')) / Sum('stock_quantity')
        )

        productSold = OrderItem.objects.filter(product=product).aggregate(
            answer=Sum('quantity')
        )

        remainingQuantity = productPurchased['quantityAlreadyPurchased'] - \
            productSold['answer']

        storestateItems.append({
            "product": ProductSerializer(product, many=False).data,
            "totalQuantity":  productPurchased['quantityAlreadyPurchased'],
            "remainingQuantity": remainingQuantity,
            "countTimesPurchased": productPurchased['countTimesPurchased']
        })

    recentsServices = ServiceOrderItem.objects.all().order_by('-id')[:2]

    
    # Year expenses, debts, revenus
    yearByFilter = datetimeconverter.strptime(
        filterDate, '%Y-%m-%d').strftime("%Y")  
    
    monthyAnalysisData = []
    for number in range(1, 13):
        payments = 0
        costPaymentOrder = Payment.objects.filter(payment_date__year=yearByFilter, payment_date__month=number).aggregate(
            answer=Sum('amount_paid')
        )

        if not costPaymentOrder['answer']:
            costPaymentOrder['answer'] = 0

        costOrdersMonth = OrderItem.objects.filter(customerOrder__order_date__year=yearByFilter, customerOrder__order_date__month=number).aggregate(
            answer=Sum(F('quantity') * F('unit_price')))

        if not costOrdersMonth['answer']:
            costOrdersMonth['answer'] = 0

        costServiceOrdersMonth = ServiceOrderItem.objects.filter(customerOrder__order_date__year=yearByFilter, customerOrder__order_date__month=number).aggregate(
            answer=Sum('total_price')
        )

        if not costServiceOrdersMonth['answer']:
            costServiceOrdersMonth['answer'] = 0

        costOrderMonth = costServiceOrdersMonth['answer'] + \
            costOrdersMonth['answer']
        difference = abs(costOrderMonth - costPaymentOrder['answer'])
        monthyAnalysisData.append(
            {
                "costOrderMonth": costOrderMonth,
                "costPaymentOrder": costPaymentOrder['answer'],
                "Difference": difference,
                "Month": get_month_name(number)
            }
        )

    context = {
        "totalOrderDebts": costOfCostOrders-totalOrderPayments,
        "Payments": totalOrderPayments,
        'costOfCostOrders': costOfCostOrders,
        "clients":  orderClients.values('customer_id').distinct().count(),
        'storestateItems': storestateItems,
        "recentsServices": ServiceOrderItemSerializer(recentsServices, many=True).data,
        "monthyAnalysisData": monthyAnalysisData
    }

    return Response(context, status=status.HTTP_200_OK)


@ api_view(["GET"])
@ permission_classes([permissions.IsAdminUser])
def customer_order_item(request, order_item_id):
    to_date_measure = request.query_params.get('date_measure')
    customer = request.query_params.get('customer')
    to_order_date = request.query_params.get('order_date')
    to_print = request.query_params.get('print')
    orders = CustomOrder.objects.all()
    if customer:
        orders.filter(
            customer__id=customer
        )

    if to_order_date:
        orders = DateUtils.handleObjectDate(
            orders, to_order_date, "order_date", to_date_measure)

    orderIdsDict = orders.filter(typeOrder=False).values('id').distinct()
    orderIds = [item['id'] for item in orderIdsDict]

    customers_items = CustomOrderItem.objects.filter(
        customerOrder__id__in=orderIds
    )
    result = []
    totalQuantityAll = 0
    totalPriceAll = 0
    totalPriceSoldAll = 0
    for item in customers_items:
        customerFound = CustomOrder.objects.filter(
            id=item.customerOrder.id
        ).values('order_date', 'customer__name')
        nameCustomer = customerFound[0]['customer__name']
        dateOrder = customerFound[0]['order_date']
        productPurchased = ProductPurchasedSerializer(
            item.productPurchased).data
        pua = float(productPurchased['unit_price'])
        quantity = item.quantity
        totalPrice = pua * float(quantity)
        titleName = productPurchased['product']['name']
        totalPriceSold = float(quantity) * float(item.unit_price)
        returnAmount = totalPriceSold - totalPrice
        puasold = item.unit_price
        result.append({
            "nameCustomer": nameCustomer,
            "dateOrder": dateOrder,
            "productTitle": titleName,
            "pua": pua,
            "quantity": quantity,
            "totalPrice": round(totalPrice, 3),
            "puasold": puasold,
            "totalPriceSold": round(totalPriceSold, 3),
            "result":  round(returnAmount, 3)
        })
        totalQuantityAll += quantity
        totalPriceAll += totalPrice
        totalPriceSoldAll += totalPriceSold
    content = {
        "result": result,
        "totalQuantityAll": round(totalQuantityAll, 3),
        "totalPriceAll": round(totalPriceAll, 3),
        "totalPriceSoldAll": round(totalPriceSoldAll, 3),
        "resultAll": round((totalPriceSoldAll - totalPriceAll), 3)
    }

    if to_print == "True":
        # Load the HTML template
        template = get_template('reports/result_unit_product.html')

        # Construct the base URL for static files
        base_url = request.build_absolute_uri(settings.STATIC_URL)

        # we add to the content the baseurl value
        content['base_url'] = base_url

        html_content = template.render(content)

        # Generate PDF using WeasyPrint
        pdf_file = HTML(string=html_content, base_url=base_url).write_pdf()

        # Create and return the PDF response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="etatVente.pdf"'
        return response

    return Response(content, status=status.HTTP_200_OK)


@ api_view(["GET"])
@ permission_classes([permissions.IsAdminUser])
def storestatepurchased(request):
    datefrom = request.query_params.get('datefrom')
    dateto = request.query_params.get('dateto')
    selectedProduct = request.query_params.get('selectedProduct')
    page = request.query_params.get('page')
    perpage = request.query_params.get('perpage')
    products = Product.objects.all()
    len(products)
    OrderItems = OrderItem.objects.all()
    if datefrom:
        OrderItems = OrderItems.filter(customerOrder__created_at__gte=datefrom)
    if dateto:
        OrderItems = OrderItems.filter(customerOrder__created_at__lte=dateto)
    results = []

    if selectedProduct:
        OrderItems = OrderItems.filter(
            product__id=selectedProduct
        )

    for item in products:
        totalQty = ProductPurchased.objects.filter(
            product__id=item.id
        ).aggregate(answer=Sum('stock_quantity'))

        quantitySold = OrderItems.filter(
            product__id=item.id
        ).aggregate(answer=Sum('quantity'))

        results.append(
            {
                "product": ProductSerializer(item, many=False).data,
                "totalQty": totalQty['answer'],
                "quantitySold": quantitySold['answer'],
            }
        )

        # Apply pagination
        # Use 10 as default if perpage is not provided
        perpage_int = int(perpage) if perpage else 10
        paginator = Paginator(results, perpage_int)
        page_obj = paginator.get_page(page)

        context = {
            "results": page_obj.object_list,
            "count": paginator.count
        }

    return Response(context, status=status.HTTP_200_OK)


@ api_view(["GET"])
@ permission_classes([permissions.IsAdminUser])
def storestate(request):
    datefrom = request.query_params.get('datefrom')
    dateto = request.query_params.get('dateto')
    selectedProduct = request.query_params.get('selectedProduct')
    methodValueStore = request.query_params.get('methodValueStore')
    productsPurchased = ProductPurchased.objects.all()
    OrderItems = OrderItem.objects
    if datefrom:
        OrderItems = OrderItems.filter(
            customerOrder__order_date__gte=datefrom,
        )

    if selectedProduct:
        OrderItems = OrderItems.filter(
            product__id=selectedProduct
        )

    if dateto:
        OrderItems = OrderItems.filter(
            customerOrder__order_date__lte=dateto
        )

    orderItemLeavingCost = []

    for orderitem in OrderItems.all():
        storeremaining = orderitem.quantity
        itemsProd = []
        if (methodValueStore == 'FIFO'):
            itemsProd = productsPurchased.filter(
                product=orderitem.product, created_at__lte=orderitem.customerOrder.order_date).all().order_by('created_at')
        else:
            itemsProd = productsPurchased.filter(
                product=orderitem.product, created_at__lte=orderitem.customerOrder.order_date).all()

        itemsLength = itemsProd.count()
        orderItemsLeaving = []
        while (storeremaining > 0 and itemsLength > -1):
            left = itemsProd[itemsLength-1].stock_quantity - storeremaining
            if (left > 0):
                orderItemsLeaving.append(
                    {'qty': storeremaining, "itemPropurchased": itemsProd[itemsLength-1].id, 'unit_price': itemsProd[itemsLength-1].unit_price})
                storeremaining -= storeremaining
                break
            else:
                orderItemsLeaving.append(
                    {'qty': itemsProd[itemsLength-1].stock_quantity,
                     'unit_price': itemsProd[itemsLength-1].unit_price})
                storeremaining -= itemsProd[itemsLength-1].stock_quantity
            itemsLength -= 1
        serialized_orderitem = OrderItemSerializer(orderitem).data
        orderItemLeavingCost.append({
            'orderitem': serialized_orderitem,
            'leavingCostItems': orderItemsLeaving
        })

    context = {
        "orderItemLeavingCost": orderItemLeavingCost,
        'productsPurchased': ProductPurchasedSerializer(productsPurchased, many=True).data,
        "count": len(orderItemLeavingCost)
    }

    return Response(context, status=status.HTTP_200_OK)


@ api_view(["GET"])
@ permission_classes([permissions.IsAdminUser])
def products_analysis(request):
    to_category = request.query_params.get('category')
    to_date_measure = request.query_params.get('date_measure')
    to_created_at = request.query_params.get('created_at')
    # State of the stock
    products = Product.objects.all()

    # if with choose specific category of product
    if to_category:
        products = products.filter(
            category__id=to_category
        )

    productsPurchased = ProductPurchased.objects.all()
    if to_created_at:

        productsPurchased = DateUtils.handleObjectDate(
            productsPurchased, to_created_at, "created_at", to_date_measure)
        if not productsPurchased:
            return Response({"Message": "any item found"}, status=status.HTTP_200_OK)

    result = []

    for product in products:
        # analyze the purchasement
        # we cheak how many fields have already been sold
        productPurchased = productsPurchased.filter(
            product__id=product.id
        ).aggregate(quantityAlreadyPurchased=Sum('stock_quantity'),
                    countTimesPurchased=Count('id'),
                    totalAmountPurchased=Sum(
            F('unit_price') * F('stock_quantity')),

            averageUnitPrice=Sum(
                F('unit_price') * F('stock_quantity')) / Sum('stock_quantity')
        )
        result.append({
            "product": ProductSerializer(product).data,
            "totalQuantity":  productPurchased['quantityAlreadyPurchased'],
            "averageUnitPrice":  productPurchased['averageUnitPrice'],
            "totalAmountPurchased":  productPurchased['totalAmountPurchased'],
            "countTimesPurchased": productPurchased['countTimesPurchased']
        })

        # This will give you the annotations for each distinct product

    return Response(result, status=status.HTTP_200_OK)


class ServiceOrderItemViewSet(viewsets.ModelViewSet):
    queryset = ServiceOrderItem.objects.all()
    serializer_class = ServiceOrderItemSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = ('description', 'category')
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminUser]


class ServiceOrderAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, format=None):
        datelimitleft = request.query_params.get('datelimitleft')
        datelimitright = request.query_params.get('datelimitright')
        customer = request.query_params.get('customer')
        category = request.query_params.get('category')
        perpage = request.query_params.get('perpage', default=5)
        page = request.query_params.get('page', default=1)
        idOrder = request.query_params.get('id')

        if idOrder is not None:
            try:
                order = CustomOrder.objects.get(id=idOrder)
                serializer = ServiceOrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except CustomOrder.DoesNotExist:
                return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            orders = CustomOrder.objects.select_related(
                'customer').all().filter(typeOrder=True)

            if customer:
                orders.filter(
                    customer=customer
                )
            if category:
                orders.filter(
                    category=category
                )

            if datelimitleft:
                orders = orders.filter(order_date__gte=datelimitleft)
            if datelimitright:
                orders = orders.filter(order_date__lte=datelimitright)

            count = len(orders)

            orders = ClassPagination.customize(perpage, page, orders)
            serializer = ServiceOrderSerializer(orders, many=True)
            locale.setlocale(locale.LC_TIME, 'fr_FR.utf8')
            current_date = datetime.now().strftime("%A %d %B %Y")

            context = {
                "orders": serializer.data,
                "count": count,
                "current_date": current_date
            }

        return Response(context, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = ServiceOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewset(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    ordering_fields = ['name', "description"]
    search_fields = ['name']
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminUser]


class CustomerViewset(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-id')
    serializer_class = CustomSerializer
    ordering_fields = ['name']
    search_fields = ['name']
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminUser]


class CustomerOrderViewset(viewsets.ModelViewSet):
    queryset = CustomOrder.objects.all()
    serializer_class = CustomOrderSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAdminUser]


@ transaction.atomic
@ api_view(["GET", "PUT", "DELETE", "POST"])
@ permission_classes([permissions.IsAdminUser])
def custom_ordering(request):
    if request.method == 'GET':
        orders = CustomOrder.objects.select_related(
            'customer').all().filter(typeOrder=False)
        to_order_date = request.query_params.get('order_date')
        to_date_measure = request.query_params.get('date_measure')
        customer = request.query_params.get('customer')
        to_productPurchased = request.query_params.get('productPurchased')
        perpage = request.query_params.get('perpage', default=5)
        page = request.query_params.get('page', default=1)

        if customer:
            orders.filter(customer=customer)
        if to_order_date:
            orders = DateUtils.handleObjectDate(
                orders, to_order_date, "order_date", to_date_measure)
        count = len(orders)
        orders = ClassPagination.customize(perpage, page, orders)

        serializerResponse = CustomOrderSerializer(
            orders, many=True)

        # If the user specify the item, for ex: voiture
        if to_productPurchased:
            orderResulted = []
            for order in serializerResponse.data:
                orderitem = []
                for item in order['order_items']:
                    if item['productPurchased'] == int(to_productPurchased):
                        orderitem.append(item)
                order['order_items'] = orderitem
                if len(orderitem) > 0:
                    orderResulted.append(order)
            return Response(orderResulted)

        return Response(
            {"orders": serializerResponse.data,
             "count": count
             }
        )
    if request.method == 'POST':
        data = request.data
        client_data = json.loads(data.get("customer"))
        deadline = request.data.get('deadline')
        customer = ''
        isCustomerToDelete = ''

        if client_data:
            # If client data is provided, check if the client exists
            client_name = client_data.get("name")
            client_id = client_data.get("id")
            client_phone_number = client_data.get("phoneNumber")
            client_adresse = client_data.get("adresse")
            try:
                customer = Customer.objects.get(
                    id=client_id)
            except Customer.DoesNotExist:
                # If client doesn't exist, create a new one
                customer = Customer.objects.create(
                    name=client_name, adresse=client_adresse, phoneNumber=client_phone_number)
                isCustomerToDelete = customer
        else:
            # If no client data provided, assume a default or anonymous client
            customer = None  # Or use a default client if needed
            return Response({"data ": "customer not provided"}, 404)

        serializer = CustomOrderSerializer(data=request.data)
        items_purchased = data.get('order_items')
        totalMountComputed = 0

        if not int(len(items_purchased) > 0):
            return Response({"data": "items purchased not provided"}, 404)

        for item_data in items_purchased:
            id = item_data['productPurchased_id']
            quantityOrdered = item_data['quantity']
            unit_price = item_data['unit_price']
            quantityAlreadySold = 0

            quantityItemPurchased = ProductPurchased.objects.get(
                pk=id).stock_quantity

            sameItemsAlreadySold = CustomOrderItem.objects.filter(
                productPurchased=id).aggregate(quantityAlreadySold=Sum('quantity'),
                                               countItems=Count('id'))
            if sameItemsAlreadySold['countItems'] >= 1:
                quantityAlreadySold = sameItemsAlreadySold['quantityAlreadySold']

            # print((quantityItemPurchased)+(quantityAlreadySold))
            if (quantityOrdered > (quantityItemPurchased)+(quantityAlreadySold)):
                product = ProductPurchased.objects.get(
                    pk=id).product
                message = f"Quantity product {product}#{id} requested is not sufficient"

                if isCustomerToDelete != '':
                    isCustomerToDelete.delete()
                return Response({"response": message}, 404)
            totalMountComputed += float(unit_price) * float(quantityOrdered)

        try:
            if int(deadline) >= 0:
                deadline = int(deadline)
        except:
            return Response({"response": "The deadline must be an integer value false"}, 404)

        if serializer.is_valid():
            serializer.save(customer=customer, deadline=deadline,
                            total_amount=totalMountComputed)
        else:
            if isCustomerToDelete != '':
                isCustomerToDelete.delete()
            serializer.is_valid(raise_exception=True)

        # You can perform additional operations if needed
        return Response(serializer.data, status.HTTP_201_CREATED)


@ transaction.atomic
@ api_view(["PUT", "DELETE"])
@ permission_classes([permissions.IsAdminUser])
def orderItemModification(request, order_id):
    # Pull up the product whose orderItem is
    orderItem = OrderItem.objects.filter(pk=order_id).get()
    if request.method == 'PUT':
        # Let me evaluate the quantity available of the same product
        # First select the order concerned by that orderItem
        quantityOrdered = request.query_params.get('quantity')
        upOrdered = request.query_params.get('unit_price')

        productData = orderItem.product

        # Then in the purchased if I still have the quantity updated, ordered or requested
        quantityInStock = ProductPurchased.objects.filter(
            product__id=productData.id).aggregate(answer_stock=Sum('stock_quantity', output_field=FloatField()))

        quantityAlreadySold = OrderItem.objects.filter(
            product=productData).exclude(id=orderItem.id).aggregate(answer_sold=Sum('quantity', output_field=FloatField()))

        presentQuantity = transfomNonetype(
            quantityInStock['answer_stock']) + transfomNonetype(quantityAlreadySold['answer_sold']) - transfomNonetype(float(quantityOrdered))

        if (presentQuantity < 0):
            return Response({f"The store of {productData.name}#{productData.id} is only {quantityInStock['answer_stock']}. Please order less than or equal to that"}, status=status.HTTP_400_BAD_REQUEST)
        orderItem.quantity = quantityOrdered
        orderItem.unit_price = upOrdered
        orderItem.save()
        # To output to the value to server client I have to serialize it, meaning put it in the right formatted way.
        serializerResponse = OrderItemSerializer(
            orderItem, many=False)
        return Response(serializerResponse.data, status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        orderItem.delete()
        return Response({'delete': f'OrderItem#{orderItem.id} deleted successfully '}, status.HTTP_202_ACCEPTED)


def transfomNonetype(value):
    if value == None:
        return 0
    else:
        return value

# override the order codes


@ api_view(["GET", "PUT", "DELETE", "POST"])
@ permission_classes([permissions.IsAdminUser])
def ordering(request):
    if request.method == 'GET':
        orders = CustomOrder.objects.select_related(
            'customer').all().filter(typeOrder=False)
        to_order_date = request.query_params.get('order_date')
        to_date_measure = request.query_params.get('date_measure')
        datelimitleft = request.query_params.get('datelimitleft')
        datelimitright = request.query_params.get('datelimitright')
        customer = request.query_params.get('customer')
        product = request.query_params.get('product')
        perpage = request.query_params.get('perpage', default=5)
        page = request.query_params.get('page', default=1)

        if datelimitleft:
            orders = orders.filter(order_date__gte=datelimitleft)
        if datelimitright:
            orders = orders.filter(order_date__lte=datelimitright)
        if customer:
            orders = orders.filter(customer=customer)
        if to_order_date:
            orders = DateUtils.handleObjectDate(
                orders, to_order_date, "order_date", to_date_measure)

        if product:
            ordersSelected = []
            product = Product.objects.get(pk=product)
            for order in orders:
                numberOfItems = OrderItem.objects.filter(
                    customerOrder=order, product=product).all().count()
                if (numberOfItems > 0):
                    ordersSelected.append(order)
            orders = ordersSelected

        count = len(orders)
        orders = ClassPagination.customize(perpage, page, orders)

        serializerResponse = OrderSerializer(
            orders, many=True)
        return Response(
            {"orders": serializerResponse.data,
             "count": count
             }
        )

    if request.method == 'POST':
        data = request.data
        deadline = request.data.get('deadline')
        orders = data.get('list_of_order_items')
        created_at = request.data.get('created_at')
        customerData = ''
        isCustomerToDelete = ''
        client_id = data.get('customer_id')
        if client_id:
            # If client data is provided, check if the client exists
            # client_name = client_data['name']
            # client_phone_number = client_data.get("phoneNumber")
            # client_adresse = client_data.get("adresse")
            try:
                customerData = Customer.objects.get(
                    id=client_id)
            except Customer.DoesNotExist:
                # If client doesn't exist, create a new one
                customerData = Customer.objects.create(
                    name='Unknown Client', adresse='Defautlt Adress', phoneNumber=' ')
                isCustomerToDelete = customerData
        else:
            # If no client data provided, assume a default or anonymous client
            customerData = None  # Or use a default client if needed
            return Response({"data ": "customer not provided"}, 404)

        items_ordered = data.get('list_of_order_items')

        if not int(len(items_ordered) > 0):
            return Response({"data": "No items provided"}, 404)

        for item_data in items_ordered:
            try:
                productData = Product.objects.get(pk=item_data['product_id'])
            except Product.DoesNotExist:
                return Response({"message": f"Product of id {item_data['product_id']} doesn't exist"}, status=status.HTTP_404_NOT_FOUND)

            quantityOrdered = item_data['quantity']
            unit_price = item_data['unit_price']
            quantityAlreadySold = 0.0
            quantityInStock = 0.0

            quantityInStock = ProductPurchased.objects.filter(
                product=productData).aggregate(answer_stock=Sum('stock_quantity', output_field=FloatField()))

            quantityAlreadySold = OrderItem.objects.filter(
                product=productData).aggregate(answer_sold=Sum('quantity', output_field=FloatField()))
            presentQuantity = transfomNonetype(
                quantityInStock['answer_stock']) + transfomNonetype(quantityAlreadySold['answer_sold']) - quantityOrdered
            if (presentQuantity < 0):
                return Response({"response": f"The store of {productData.name}#{productData.id} is only {quantityInStock}, please order less than or equal to {presentQuantity} of   is unsufficient"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if int(deadline) >= 0:
                deadline = int(deadline)
        except:
            return Response({"response": "The deadline must be an integer value false"}, status=Http404)
        # order-item/<int:order_id>/
        # data['list_of_order_items']=)
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customerData,
                            created_at=created_at, deadline=deadline)
        else:
            if isCustomerToDelete != '':
                isCustomerToDelete.delete()
            serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status.HTTP_201_CREATED)
    if request.method == 'DELETE':
        idOrder = request.query_params.get('idOrder')
        OrderToDelete = CustomOrder.objects.filter(pk=idOrder).get()
        if (OrderToDelete.typeOrder == False):
            OrderItem.objects.filter(
                customerOrder=OrderToDelete).all().delete()
        else:
            ServiceOrderItem.objects.filter(
                customerOrder=OrderToDelete).all().delete()
        OrderToDelete.delete()
        return Response({'Delete': f'Order#{OrderToDelete.id} deleted successfully '}, status.HTTP_202_ACCEPTED)
    if request.method == 'PUT':
        # here we just perfom a partial edit
        idOrder = request.data.get('id')
        deadline = request.data.get('deadline')
        customerid = request.data.get('customer_id')
        date = request.data.get('date')
        OrderToEdit = CustomOrder.objects.filter(pk=idOrder).get()
        OrderToEdit.customer = Customer.objects.filter(pk=customerid).get()
        OrderToEdit.deadline = deadline
        OrderToEdit.order_date = date
        OrderToEdit.save()
        OrderToEdit = CustomOrder.objects.filter(pk=idOrder).get()
        return Response({'Edit': f'Order#{OrderToEdit.id} edited successfully '}, status.HTTP_200_OK)


class CustomOrderAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            order = CustomOrder.objects.get(id=pk)
            serializer = CustomOrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomOrder.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            customerorder = CustomOrder.objects.get(pk=pk)
        except CustomOrder.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        items_purchased = request.data.get('order_items')
        deadline = request.data.get('deadline')
        totalMountComputed = 0

        for item_data in items_purchased:
            id = item_data['productPurchased']

            quantityOrdered = item_data['quantity']
            unit_price = item_data['unit_price']
            quantityAlreadySold = 0

            quantityItemPurchased = ProductPurchased.objects.get(
                pk=id).stock_quantity

            sameItemsAlreadySold = CustomOrderItem.objects.filter(
                productPurchased=id).aggregate(quantityAlreadySold=Sum('quantity'),
                                               countItems=Count('id'))

            if sameItemsAlreadySold['countItems'] >= 1:
                quantityAlreadySold = sameItemsAlreadySold['quantityAlreadySold']

            # print((quantityItemPurchased)+(quantityAlreadySold))
            if (quantityOrdered > float((quantityItemPurchased)) + float((quantityAlreadySold)) - float((quantityOrdered))):
                product = ProductPurchased.objects.get(
                    pk=id).product
                message = f"Quantity product {product.name}#{id} requested is not sufficient"
                return Response({"response": message}, 404)
            totalMountComputed += float(unit_price) * float(quantityOrdered)

        customerorder.total_amount = totalMountComputed
        if not isinstance(deadline, int):
            return Response({"response": "The deadline must be an integer value"}, 404)

        customerorder.deadline = abs(deadline)
        customerorder.save()

        itemsAlreadyPurchased = CustomOrderItem.objects.filter(
            customerOrder=pk
        )

        itemsAlreadyPurchasedSought = [
            item.id for item in itemsAlreadyPurchased]

        for order_item in items_purchased:
            if order_item['id'] in itemsAlreadyPurchasedSought:
                item = CustomOrderItem.objects.get(pk=order_item['id'])
                # if item in items_purchased:
                item.quantity = order_item['quantity']
                item.unit_price = order_item['unit_price']
                item.description = order_item['description']
                item.save()
        serializerResponse = CustomOrderSerializer(
            customerorder, many=False)
        return Response(serializerResponse.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            customerOrder = CustomOrder.objects.get(
                id=pk)
            customerOrder.delete()
            return Response({"message": f"Order#{id} deleted"}, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"message": "Order not found"}, status=404)


@ api_view(["GET"])
@ permission_classes([permissions.IsAdminUser])
def report_print(request, pk):
    typeOrder = request.GET.get('typeOrder')
    orderToReport = []
    if typeOrder is None:
        return Response({"message": "Type Order not specified"}, status=status.HTTP_404_NOT_FOUND)
    else:
        try:
            order = CustomOrder.objects.get(id=pk)
        except CustomOrder.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        if typeOrder.lower() == 'true':
            customerOrder = ServiceOrderSerializer(order)
            orderToReport = customerOrder.data
        else:
            customerOrder = CustomOrderSerializer(order)
            orderToReport = customerOrder.data

        # Load the HTML template
        template = get_template('reports/order.html')

        # Construct the base URL for static files
        base_url = request.build_absolute_uri(settings.STATIC_URL)
        context = {'order': orderToReport,
                   'base_url': base_url, 'typeOrder': typeOrder}
        html_content = template.render(context)

        # Generate PDF using WeasyPrint
        pdf_file = HTML(string=html_content, base_url=base_url).write_pdf()

        # Create and return the PDF response
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="report.pdf"'
        return response
