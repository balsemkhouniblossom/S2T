from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    path('', views.moderation_dashboard, name='dashboard'),
    path('pending/', views.pending_reports, name='pending_reports'),
    path('report/<int:report_id>/', views.review_report, name='review_report'),
    path('stats/', views.moderation_stats, name='stats'),
    path('test/', views.test_content, name='test_content'),
    path('api/moderate/', views.api_moderate_content, name='api_moderate'),
    path('admin/complaints/', views.admin_complaints_list, name='admin_complaints_list'),
]
