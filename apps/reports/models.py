from django.db import models
from django.conf import settings
from apps.orders.models import Order
from apps.products.models import Product

class Report(models.Model):
    REPORT_TYPES = (
        ('order', 'Order Issue'),
        ('product', 'Product Issue'),
        ('shipping', 'Shipping Issue'),
        ('other', 'Other Issue')
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    )
    
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Report #{self.id} - {self.get_report_type_display()}"

    class Meta:
        ordering = ['-created_at']