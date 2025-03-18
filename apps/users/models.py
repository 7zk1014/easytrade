from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('both', 'Buyer & Seller'),  # 添加新的角色选项
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='both')  # 修改默认值为 both
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # 添加头像字段

    def __str__(self):
        return self.username
