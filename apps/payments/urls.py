from django.urls import path
from .views import (
    create_payment_intent, payment_history, recharge_balance,
    request_refund, view_refund_request, process_refund, my_refund_requests
)

urlpatterns = [
    path('create_intent/', create_payment_intent, name='create_payment_intent'),
    path('history/', payment_history, name='payment_history'),
    path('recharge/', recharge_balance, name='recharge_balance'),
    path('refund/request/<int:order_id>/', request_refund, name='request_refund'),
    path('refund/view/<int:request_id>/', view_refund_request, name='view_refund_request'),
    path('refund/process/<int:request_id>/', process_refund, name='process_refund'),
    path('refund/my-requests/', my_refund_requests, name='my_refund_requests'),
]
