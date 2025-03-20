from django.test import TestCase
from django.urls import reverse
from apps.users.models import CustomUser
from apps.products.models import Product
from .models import CartItem
from decimal import Decimal

class CartTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create seller user
        self.seller = CustomUser.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='sellerpassword'
        )
        
        # Create test product
        self.product = Product.objects.create(
            title='Test Product',
            description='This is a test product',
            price=99.99,
            seller=self.seller,
            category='Electronics'
        )
        
        # Login user
        self.client.login(username='testuser', password='testpassword')
    
    def test_add_to_cart(self):
        """Test adding product to cart"""
        # Send add to cart request
        response = self.client.post(reverse('add_to_cart'), {
            'product_id': self.product.id,
            'quantity': 2
        })
        
        # Check if redirected
        self.assertEqual(response.status_code, 302)
        
        # Check cart item in database
        cart_item = CartItem.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart_item.quantity, 2)
        
        # Check cart total price
        self.assertEqual(cart_item.total_price, Decimal('199.98'))
    
    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        # First add product to cart
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=1
        )
        
        # Send update cart request
        response = self.client.post(reverse('update_cart_item', args=[cart_item.id]), {
            'quantity': 3
        })
        
        # Check if redirected
        self.assertEqual(response.status_code, 302)
        
        # Check if cart data was updated in database
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)
    
    def test_remove_from_cart(self):
        """Test removing product from cart"""
        # First add product to cart
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=1
        )
        
        # Send remove from cart request
        response = self.client.post(reverse('remove_from_cart', args=[cart_item.id]))
        
        # Check if redirected
        self.assertEqual(response.status_code, 302)
        
        # Check if product was removed from cart
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
    
    def test_update_cart_quantity_to_zero(self):
        """Test updating cart item quantity to zero (equivalent to removing)"""
        # First add product to cart
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=1
        )
        
        # Send update cart request with quantity=0
        response = self.client.post(reverse('update_cart_item', args=[cart_item.id]), {
            'quantity': 0
        })
        
        # Check if redirected
        self.assertEqual(response.status_code, 302)
        
        # Check if product was removed from cart
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
    
    def test_view_cart(self):
        """Test viewing cart"""
        # Add product to cart
        cart_item = CartItem.objects.create(
            user=self.user,
            product=self.product,
            quantity=2
        )
        
        # Visit cart page
        response = self.client.get(reverse('view_cart'))
        
        # Check if page loaded successfully
        self.assertEqual(response.status_code, 200)
        
        # Check if product is displayed in cart
        self.assertContains(response, self.product.title)
        
        # Check if quantity is displayed correctly
        self.assertContains(response, 'value="2"')
    
    def test_buy_now(self):
        """Test buy now functionality"""
        # Send buy now request
        response = self.client.post(reverse('buy_now'), {
            'product_id': self.product.id,
            'quantity': 1
        })
        
        # Check if redirected to checkout page
        self.assertEqual(response.status_code, 302)
        
        # Check if redirected to checkout with buy_now parameter
        self.assertIn(f"?buy_now={self.product.id}", response.url)
        
        # Check if cart item was created
        self.assertTrue(CartItem.objects.filter(
            user=self.user,
            product=self.product,
            quantity=1
        ).exists())