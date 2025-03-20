from django.urls import path
from .views import PostProductView

urlpatterns = [
    path('', PostProductView.as_view(), name='post_product'),
]
