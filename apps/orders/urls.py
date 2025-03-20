from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()
router.register(r'', OrderViewSet, basename='order')

from django.urls import path
from . import views

# 移除seller_orders路由，保留ship_order和complete_order路由
urlpatterns = [
    path('', include(router.urls)),
    path('orders/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    # 确保没有这一行：path('seller-orders/', views.seller_orders, name='seller_orders'),
    path('ship-order/<int:order_id>/', views.ship_order, name='ship_order'),
    path('complete-order/<int:order_id>/', views.complete_order, name='complete_order'),
    path('help/', views.order_help, name='order_help'),
]
