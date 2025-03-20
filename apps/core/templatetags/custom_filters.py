from django import template
from apps.orders.models import Order

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to access dictionary values by key
    Usage: {{ my_dict|get_item:key_variable }}
    """
    return dictionary.get(key)


@register.filter
def currency(value):
    """Format value as currency"""
    try:
        # Convert to float if it's a string
        if isinstance(value, str):
            value = float(value)
        return f"£{float(value):.2f}"
    except (ValueError, TypeError):
        # If conversion fails, return the original value with £ symbol
        return f"£{value}"

@register.filter
def status_badge(status):
    status_classes = {
        'pending': 'warning',
        'paid': 'success',
        'shipped': 'info',
        'delivered': 'primary',
        'cancelled': 'danger',
        'refunded': 'secondary'
    }
    return status_classes.get(status.lower(), 'secondary')

@register.filter
def multiply(value, arg):
    return float(value) * arg


@register.filter
def can_review_product(user, product):
    """Check if user can review a product"""
    if not user.is_authenticated:
        return False
    
    return Order.objects.filter(
        buyer=user,
        status__in=['completed', 'delivered'],
        items__product=product
    ).exists()


@register.filter
def filter_by_status(products, status):
    """Filter products by specified status"""
    return [p for p in products if p.status == status]

@register.filter
def exclude_by_status(products, status):
    """Exclude products with specified status"""
    return [p for p in products if p.status != status]