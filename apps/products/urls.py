from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from .views import my_products_view
from django.urls import path
from . import views  

router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns = [
    path('my-products/', my_products_view, name='my_products'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
]