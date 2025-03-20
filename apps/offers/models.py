from django.db import models
from apps.users.models import CustomUser
from apps.products.models import Product

OFFER_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
)

class Offer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='offers')
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='offers')
    offer_price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    offer_status = models.CharField(max_length=10, choices=OFFER_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Offer of ${self.offer_price} on {self.product.title} by {self.buyer.username}"
    
    def get_offer_status_display(self):
        return dict(OFFER_STATUS_CHOICES).get(self.offer_status, self.offer_status)
