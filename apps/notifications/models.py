from django.db import models
from django.conf import settings
from apps.products.models import Product
from apps.orders.models import Order

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('product_sold', 'Product Sold'),
        ('new_order', 'New Order'),
        ('order_status', 'Order Status Update'),
        ('message', 'New Message'),
        ('review', 'New Review'),
        ('refund_requested', 'Refund Requested'),
        ('refund_approved', 'Refund Approved'),
        ('refund_rejected', 'Refund Rejected'),
        ('refund_completed', 'Refund Completed'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='custom_notifications'  # 修改这里，使用唯一的related_name
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    related_order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"