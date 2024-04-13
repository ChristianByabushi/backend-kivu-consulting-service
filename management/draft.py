@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def payment_analysis(request):
    # I select the all orders that have already been purchased by the customer
    customer_order_ids = Customer.objects.annotate(
        customer_order_id=F('order_Purchased__id')
    ).values('customer_order_id').distinct()

    # i groupby, annotate the orders found and summ the amount_paid
    aggretated_arguments = Payment.objects.filter(
        purchase_order__id__in=customer_order_ids
    ).annotate(
        total_paid=Sum('amount_paid')
    )
    result = []

    query &= (
        Q(**{f"{datefield}__gte": start_date}) &
        Q(**{f"{datefield}__lte": end_date}) &
        Q(**{f"other_field__icontains": "some_value"})
    )


    # Assuming productsPurchased is your queryset
    product_purchased_annotations = productsPurchased.values('product__id').distinct().annotate(
        quantityAlreadyPurchased=Sum('stock_quantity'),
        countTimesPurchased=Count('id'),
        totalAmountPurchased=Sum(
            ExpressionWrapper(
                F('unit_price') * F('stock_quantity'),
                output_field=DecimalField()
            )
        )  # Coalesce handles cases where there is no purchase
    )
