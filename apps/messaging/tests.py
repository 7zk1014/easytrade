from django.test import TestCase
from django.urls import reverse
from apps.users.models import CustomUser
from apps.products.models import Product
from .models import Message

class MessagingModelTest(TestCase):
    def setUp(self):
        # Create sender and receiver
        self.sender = CustomUser.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='senderpassword'
        )
        
        self.receiver = CustomUser.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            password='receiverpassword'
        )
        
        # Create product
        self.product = Product.objects.create(
            title='Test Product',
            description='This is a test product',
            price=99.99,
            seller=self.receiver,
            category='Electronics'
        )
        
        # Create message
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content='Hello, is this product still available?'
        )
    
    def test_message_creation(self):
        """Test message creation"""
        self.assertEqual(self.message.sender, self.sender)
        self.assertEqual(self.message.receiver, self.receiver)
        self.assertEqual(self.message.content, 'Hello, is this product still available?')
        self.assertFalse(self.message.is_read)
    
    def test_mark_as_read(self):
        """Test marking message as read"""
        self.assertFalse(self.message.is_read)
        self.message.mark_as_read()
        self.assertTrue(self.message.is_read)

class MessagingViewTest(TestCase):
    def setUp(self):
        # Create sender and receiver
        self.sender = CustomUser.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='senderpassword'
        )
        
        self.receiver = CustomUser.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            password='receiverpassword'
        )
        
        # Create product
        self.product = Product.objects.create(
            title='Test Product',
            description='This is a test product',
            price=99.99,
            seller=self.receiver,
            category='Electronics'
        )
        
        # Login as sender
        self.client.login(username='sender', password='senderpassword')
    
    def test_send_message_view(self):
        """Test send message functionality"""
        # Send message request
        message_data = {
            'content': 'Hello, is this product still available?',
            'recipient_id': self.receiver.id
        }
        
        response = self.client.post(reverse('send_message'), message_data)
        
        # Check if redirected
        self.assertEqual(response.status_code, 302)
        
        # Verify if message was created
        self.assertTrue(Message.objects.filter(
            sender=self.sender,
            receiver=self.receiver,
            content='Hello, is this product still available?'
        ).exists())
    
    def test_view_messages(self):
        """Test view messages list"""
        # Create some messages
        Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content='Yes, it is still available.'
        )
        
        Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content='Are you interested in buying?'
        )
        
        # Visit messages list page
        response = self.client.get(reverse('view_messages'))
        
        # Check if page loaded successfully
        self.assertEqual(response.status_code, 200)
        
        # Check if receiver is displayed on the page
        self.assertContains(response, self.receiver.username)
    
    def test_view_conversation(self):
        """Test view conversation"""
        # Create a conversation
        message1 = Message.objects.create(
            sender=self.receiver,
            receiver=self.sender,
            content='Yes, it is still available.'
        )
        
        # Visit conversation page
        response = self.client.get(reverse('view_conversation', args=[self.receiver.id]))
        
        # Check if page loaded successfully
        self.assertEqual(response.status_code, 200)
        
        # Check if message is displayed on the page
        self.assertContains(response, 'Yes, it is still available.')