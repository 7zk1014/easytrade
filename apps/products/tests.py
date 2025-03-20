from django.test import TestCase
from django.urls import reverse
from apps.users.models import CustomUser
from .models import Product  # Removed Category import

class ProductModelTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create test product
        self.product = Product.objects.create(
            title='Test Product',
            description='This is a test product',
            price=99.99,
            seller=self.user,
            category='electronics'
            # Removed condition and quantity fields
        )
    
    def test_product_creation(self):
        """Test if product creation is successful"""
        self.assertEqual(self.product.title, 'Test Product')
        self.assertEqual(self.product.price, 99.99)
        self.assertEqual(self.product.seller, self.user)
        self.assertEqual(self.product.status, 'active')  # Default status should be active
    
    def test_product_str_method(self):
        """Test the string representation of the product"""
        self.assertEqual(str(self.product), 'Test Product')


class ProductViewTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Login user
        self.client.login(username='testuser', password='testpassword')
        
        # Create test product - using correct category value
        self.product = Product.objects.create(
            title='Test Product',
            description='This is a test product',
            price=99.99,
            seller=self.user,
            category='Electronics'  # Changed to capitalized first letter
        )
    
    def test_create_product_view(self):
        """Test product posting page"""
        # Login user
        self.client.login(username='testuser', password='testpassword')
        
        # Use correct URL name post_product
        response = self.client.get(reverse('post_product'))
        self.assertEqual(response.status_code, 200)
        
        # Print available category options in the form for debugging
        if hasattr(response, 'context') and response.context and 'form' in response.context:
            form = response.context['form']
            if hasattr(form.fields.get('category', {}), 'choices'):
                print("Available category options:", form.fields['category'].choices)
        
        # Test product creation functionality - using correct category value (capitalized)
        product_data = {
            'title': 'New Test Product',
            'description': 'This is a new test product',
            'price': '199.99',
            'category': 'Electronics',  # Changed to capitalized first letter to match form options
            'image': '',
        }
        
        # Send POST request to post_product URL
        response = self.client.post(reverse('post_product'), product_data)
        
        # Print response content and form errors for debugging
        print("Response status code:", response.status_code)
        if hasattr(response, 'context') and response.context and 'form' in response.context:
            print("Form errors:", response.context['form'].errors.as_text())
        
        # Check if product was created in database
        created_products = Product.objects.filter(title='New Test Product')
        print("Number of created products:", created_products.count())
        
        # Verify product exists
        self.assertTrue(Product.objects.filter(title='New Test Product').exists())
        
        # Check created product attributes
        new_product = Product.objects.get(title='New Test Product')
        self.assertEqual(new_product.description, 'This is a new test product')
        self.assertEqual(float(new_product.price), 199.99)
        self.assertEqual(new_product.category, 'Electronics')  # Also need to change to capitalized first letter
        self.assertEqual(new_product.seller, self.user)
        self.assertEqual(new_product.status, 'active')
