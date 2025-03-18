from django import template

register = template.Library()

@register.filter(name='filter_status')
def filter_status(reports, status):
    """
    过滤指定状态的报告
    用法: {{ reports|filter_status:'pending' }}
    """
    return [report for report in reports if report.status == status]