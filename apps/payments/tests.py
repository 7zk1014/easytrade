from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from apps.users.models import CustomUser
from apps.orders.models import Order
from .models import Payment

class PaymentModelTest(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            balance=Decimal('100.00')
        )
        
        # 创建测试支付记录
        self.payment = Payment.objects.create(
            user=self.user,
            amount=Decimal('50.00'),
            payment_method='credit_card',
            payment_type='recharge',
            status='completed',
            transaction_id='TEST123456',
            description='Test payment'
        )
    
    def test_payment_creation(self):
        """Test payment record creation"""
        self.assertEqual(self.payment.user, self.user)
        self.assertEqual(self.payment.amount, Decimal('50.00'))
        self.assertEqual(self.payment.status, 'completed')
        self.assertEqual(self.payment.payment_type, 'recharge')

class PaymentViewTest(TestCase):
    def setUp(self):
        # 创建测试用户
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword',
            balance=Decimal('100.00')
        )
        
        # 登录用户
        self.client.login(username='testuser', password='testpassword')
    
    def test_recharge_balance_view(self):
        """Test balance recharge functionality"""
        # Get recharge page
        response = self.client.get(reverse('recharge_balance'))
        self.assertEqual(response.status_code, 200)
        
        # Test recharge function
        recharge_data = {
            'amount': '50.00',
            'payment_method': 'credit_card'
        }
        
        # Send recharge request
        response = self.client.post(reverse('recharge_balance'), recharge_data)
        
        # Check if redirected
        self.assertEqual(response.status_code, 302)
        
        # Check if user balance has been updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal('150.00'))
        
        # Check if payment record was created
        self.assertTrue(Payment.objects.filter(
            user=self.user,
            amount=Decimal('50.00'),
            payment_type='recharge',
            status='completed'
        ).exists())