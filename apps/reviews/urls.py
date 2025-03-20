from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet

router = DefaultRouter()
router.register(r'', ReviewViewSet, basename='review')

from django.urls import path
from . import views

urlpatterns = [
    path('seller/<int:seller_id>/add/', views.add_seller_review, name='add_seller_review'),
    path('seller/<int:seller_id>/all/', views.seller_reviews, name='seller_reviews'),
    path('seller/<int:seller_id>/', views.seller_profile, name='seller_profile'),  # 添加这行
    path('product/<int:product_id>/add/', views.add_review, name='add_review'),
    path('product/<int:product_id>/', views.product_reviews, name='product_reviews'),
]
