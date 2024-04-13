from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r"categories", views.CategoryViewset, basename="category")

router.register(r"products", views.ProductViewSet, basename="product")

router.register(r"suppliers", views.SupplierViewSet, basename="supplier")

# router.register(r"custom-service", views.CustomServiceOrderViewSet, basename="custom-service")

router.register(r"customers", views.CustomerViewset, basename="customer")
# router.register(r"custom-ordering", views.CustomerOrderViewset,
#                 basename="ordering")

router.register(r"products-purchased",
                views.ProductPurchasedViewSet, basename="product-purchased")

urlpatterns = [
    path("", include(router.urls)),

    path('custom-ordering/', views.custom_ordering, name="custom_ordering"),

    path('ordering/', views.ordering, name="ordering"),

    #   path('custom-ordering/<int:pk>/', views.CustomOrderAPIView.as_view()),

    #          name='customordering'),
    path('custom-service/', views.CustomServiceOrderAPIView.as_view(),
         name='custom-service-order-list'),

    path('custom-service/<int:pk>/', views.CustomServiceOrderAPIView.as_view(),
         name='custom-service-order-detail'),

    path('payment-order/', views.PaymentsOrderAPIView.as_view(),
         name='payment-order-list'),

    path('payment-order/<int:pk>/', views.PaymentsOrderAPIView.as_view(),
         name='payment-order-detail'),

    path('report-print/<int:pk>/', views.report_print, name='report_print'),

    path('payment-analysis/', views.payment_analysis, name="payment_analysis"),

    path('products-analysis/', views.products_analysis, name="products_analysis"),

    path('customer-order-items/<int:order_item_id>/', views.customer_order_item,
         name="customer_order_item_print"),

    path('order-state/<int:order_id>/', views.get_order_state,
         name="order_state"), 

    path('order-item/<int:order_id>/', views.orderItemModification,
         name="order_item"),

]
