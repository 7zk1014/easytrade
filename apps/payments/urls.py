from django.urls import path
from .views import create_payment_intent

urlpatterns = [
    path('create_intent/', create_payment_intent, name='create_payment_intent'),
]
