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
    """将数值格式化为货币格式"""
    return f"£{value:.2f}"

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
    """检查用户是否可以评价产品"""
    if not user.is_authenticated:
        return False
    
    return Order.objects.filter(
        buyer=user,
        status__in=['completed', 'delivered'],
        items__product=product
    ).exists()