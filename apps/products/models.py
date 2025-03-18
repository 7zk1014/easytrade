from django.db import models
from apps.users.models import CustomUser

class Product(models.Model):
    # 预定义的商品分类选项
    CATEGORY_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Clothing', 'Clothing'),
        ('Home', 'Home & Garden'),
        ('Books', 'Books'),
        ('Sports', 'Sports'),
        ('Collectibles', 'Collectibles'),
        ('Toys', 'Toys'),
        ('Beauty', 'Beauty & Personal Care'),
        ('Automotive', 'Automotive'),
        ('Other', 'Other')
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='Other')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('hidden', 'Hidden')
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
