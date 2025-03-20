from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from . import views

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')  # 修改这里，添加前缀

urlpatterns = [
    path('', include(router.urls)),
    path('my-products/', views.my_products, name='my_products'),  # 这个路径现在不会与API路由冲突
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
]