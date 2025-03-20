from .models import Notification

def notify_seller(product, buyer):
    """
    Create product sold notification for seller
    
    Args:
        product: The sold product
        buyer: The buyer
    """
    Notification.objects.create(
        user=product.seller,
        notification_type='product_sold',
        content=f'Your product "{product.title}" has been purchased',
        related_product=product
    )

def get_notification_message(notification):
    """
    Get notification message
    
    Args:
        notification: The notification
    """
    
    # Return related messages
    if notification.notification_type == 'requested_return':
        return f"{notification.sender.username} has requested a return for order #{notification.target_id}"