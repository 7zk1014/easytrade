from django import template

register = template.Library()

@register.filter
def status_badge(status):
    """返回与订单状态对应的Bootstrap徽章颜色类"""
    status_colors = {
        'pending': 'warning',
        'paid': 'primary',
        'shipped': 'info',
        'delivered': 'success',
        'completed': 'success',
        'cancelled': 'danger',
        'refunded': 'secondary',
    }
    return status_colors.get(status, 'secondary')