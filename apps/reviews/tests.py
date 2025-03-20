from django.test import TestCase
from django.urls import reverse
from apps.users.models import CustomUser
from apps.products.models import Product
from apps.orders.models import Order, OrderItem
from .models import Review, SellerReview

class ReviewModelTest(TestCase):
    def setUp(self):
        # Create buyer and seller
        self.buyer = CustomUser.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='buyerpassword'
        )
        
        self.seller = CustomUser.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='sellerpassword'
        )
        
        # Create product
        self.product = Product.objects.create(
            title='Test Product',
            description='This is a test product',
            price=99.99,
            seller=self.seller,
            category='Electronics'
        )
       
        # Create completed order (delivered status)
        self.order = Order.objects.create(
            buyer=self.buyer,
            status='delivered'  # Set to delivered status
        )
        
        # Create order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=self.product.price
        )
        
        # Create product review
        self.review = Review.objects.create(
            product=self.product,
            reviewer=self.buyer,
            rating=4,
            comment='Great product!',
            verified_purchase=True
        )
        
        # Create seller review
        self.seller_review = SellerReview.objects.create(
            seller=self.seller,
            reviewer=self.buyer,
            order=self.order,
            rating=5,
            comment='Excellent seller!'
        )
    
    def test_review_creation(self):
        """Test review creation"""
        self.assertEqual(self.review.product, self.product)
        self.assertEqual(self.review.reviewer, self.buyer)
        self.assertEqual(self.review.rating, 4)
        self.assertEqual(self.review.comment, 'Great product!')
        self.assertTrue(self.review.verified_purchase)
    
    def test_seller_review_creation(self):
        """Test seller review creation"""
        self.assertEqual(self.seller_review.seller, self.seller)
        self.assertEqual(self.seller_review.reviewer, self.buyer)
        self.assertEqual(self.seller_review.rating, 5)
        self.assertEqual(self.seller_review.comment, 'Excellent seller!')

class ReviewViewTest(TestCase):
    def setUp(self):
        # Create buyer and seller
        self.buyer = CustomUser.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='buyerpassword'
        )
        
        self.seller = CustomUser.objects.create_user(
            username='seller',
            email='seller@example.com',
            password='sellerpassword'
        )
        
        # Create product
        self.product = Product.objects.create(
            title='Test Product',
            description='This is a test product',
            price=99.99,
            seller=self.seller,
            category='Electronics'
        )
        
        # Create completed order (delivered status)
        self.order = Order.objects.create(
            buyer=self.buyer,
            status='delivered'  # Set to delivered status
        )
        
        # Create order item
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=self.product.price
        )
        
        # Login as buyer
        self.client.login(username='buyer', password='buyerpassword')
    
    def test_add_review_view(self):
        """Test add review functionality"""
        # Send add review request
        review_data = {
            'rating': 4,
            'comment': 'Great product, very satisfied!'
        }
        
        response = self.client.post(reverse('add_review', args=[self.product.id]), review_data)
        
        # Check if redirected
        self.assertEqual(response.status_code, 302)
        
        # Verify if review was created
        self.assertTrue(Review.objects.filter(
            product=self.product,
            reviewer=self.buyer,
            rating=4,
            comment='Great product, very satisfied!'
        ).exists())
    
    def test_add_seller_review_view(self):
        """Test add seller review functionality"""
        # Send add seller review request
        review_data = {
            'rating': 5,
            'comment': 'Excellent seller, fast shipping!'
        }
        
        # Modified: only use seller_id parameter, don't pass order_id
        response = self.client.post(reverse('add_seller_review', args=[self.seller.id]), review_data)
        
        # Check if redirected
        self.assertEqual(response.status_code, 302)
        
        # Verify if seller review was created
        self.assertTrue(SellerReview.objects.filter(
            seller=self.seller,
            reviewer=self.buyer,
            rating=5,
            comment='Excellent seller, fast shipping!'
        ).exists())
    
    def test_product_reviews_view(self):
        """Test product reviews list view"""
        # Create multiple reviews
        Review.objects.create(
            product=self.product,
            reviewer=self.buyer,
            rating=5,
            comment='Excellent product!',
            verified_purchase=True
        )
        
        # Visit product reviews page
        response = self.client.get(reverse('product_reviews', args=[self.product.id]))
        
        # Check if page loaded successfully
        self.assertEqual(response.status_code, 200)
        
        # Check if review is displayed on the page
        self.assertContains(response, 'Excellent product!')
    
    def test_seller_reviews_view(self):
        """Test seller reviews list view"""
        # Create multiple seller reviews
        SellerReview.objects.create(
            seller=self.seller,
            reviewer=self.buyer,
            order=self.order,
            rating=4,
            comment='Good seller!'
        )
        
        # Visit seller reviews page
        response = self.client.get(reverse('seller_reviews', args=[self.seller.id]))
        
        # Check if page loaded successfully
        self.assertEqual(response.status_code, 200)
        
        # Check if review is displayed on the page
        self.assertContains(response, 'Good seller!')
    
    def test_cannot_review_without_purchase(self):
        """Test that users cannot review products they haven't purchased"""
        # Create a new product that the buyer hasn't purchased
        new_product = Product.objects.create(
            title='New Product',
            description='This is a new product',
            price=149.99,
            seller=self.seller,
            category='Electronics'
        )
        
        # Try to review a product not purchased
        review_data = {
            'rating': 3,
            'comment': 'Not purchased but trying to review'
        }
        
        response = self.client.post(reverse('add_review', args=[new_product.id]), review_data)
        
        # Should redirect and show error message
        self.assertEqual(response.status_code, 302)
        
        # Verify review was not created
        self.assertFalse(Review.objects.filter(
            product=new_product,
            reviewer=self.buyer
        ).exists())