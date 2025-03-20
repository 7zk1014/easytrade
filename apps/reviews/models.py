from django.db import models
from apps.users.models import CustomUser
from apps.products.models import Product
from apps.orders.models import Order

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_purchase = models.BooleanField(default=False)  # 保留此字段，但不再作为评价的必要条件

    def __str__(self):
        return f"Review for {self.product.title} by {self.reviewer.username}"

class SellerReview(models.Model):
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='seller_reviews')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_seller_reviews')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, related_name='seller_reviews', null=True, blank=True)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # 这个字段应该已经设置了auto_now=True

    def __str__(self):
        return f"Seller review for {self.seller.username} by {self.reviewer.username}"
