from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    label = 'custom_notifications'  # 添加这一行，设置唯一的应用标签
    verbose_name = '通知管理'