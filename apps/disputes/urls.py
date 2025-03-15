from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'disputes', views.DisputeViewSet, basename='dispute')
router.register(r'dispute-messages', views.DisputeMessageViewSet, basename='dispute-message')

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),
    
    # Web URLs
    path('', views.dispute_list, name='dispute_list'),
    path('<int:dispute_id>/', views.dispute_detail, name='dispute_detail'),
    path('create/<int:order_id>/', views.create_dispute, name='create_dispute'),
    path('resolve/<int:dispute_id>/', views.resolve_dispute, name='resolve_dispute'),
    path('escalate/<int:dispute_id>/', views.escalate_dispute, name='dispute_escalate'),
]
