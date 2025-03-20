from django.db import models
from apps.users.models import CustomUser
from apps.orders.models import Order
from django.conf import settings

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('balance', 'Account Balance'),
        ('alipay', 'Alipay'),
        ('wechat', 'WeChat Pay'),
        ('card', 'Bank Card'),
        ('refund', 'Refund'), 
    )
    
    PAYMENT_TYPE_CHOICES = (
        ('purchase', 'Purchase'),
        ('sale', 'Sale'),
        ('refund', 'Refund'),
        ('recharge', 'Recharge'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='balance')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='purchase')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment #{self.id} - {self.user.username} - {self.amount} ({self.status})"


class RefundRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refund_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Refund #{self.id} for Order #{self.order.id}"

