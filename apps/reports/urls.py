from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # 删除这一行，因为 create_report 视图函数不存在
    # path('create/', views.create_report, name='create_report'),
    path('submit/', views.submit_report, name='submit_report'),
    path('list/', views.report_list, name='report_list'),
    path('detail/<int:report_id>/', views.report_detail, name='report_detail'),
    path('admin/', views.admin_report_list, name='admin_report_list'),
    path('update/<int:report_id>/', views.update_report_status, name='update_report_status'),  
]
