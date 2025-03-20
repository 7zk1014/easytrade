from apps.notifications.consumers import SellerNotificationConsumer

websocket_urlpatterns = [
    path('ws/seller-notifications/<int:seller_id>/', SellerNotificationConsumer.as_asgi()),
]