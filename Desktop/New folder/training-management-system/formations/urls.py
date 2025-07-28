from django.urls import path
from . import views

app_name = 'formations'

urlpatterns = [
    # Formation list and search
    path('', views.formations_list, name='list'),
    
    # Formation details and enrollment
    path('<int:formation_id>/', views.formation_detail, name='detail'),
    path('<int:formation_id>/enroll/', views.formation_enroll, name='enroll'),
    path('<int:formation_id>/org-enroll/', views.organisation_enroll, name='organisation_enroll'),
    path('org-enroll/confirm/<int:enrollment_id>/', views.organisation_enroll_confirm, name='organisation_enroll_confirm'),
    path('<int:formation_id>/unenroll/', views.formation_unenroll, name='unenroll'),
    
    # Formation management (for formateurs and admins)
    path('create/', views.formation_create, name='create'),
    
    # My formations
    path('my-formations/', views.my_formations, name='my_formations'),
    
    # Trainer applications
    path('opportunities/', views.available_formations, name='available_formations'),
    path('<int:formation_id>/apply/', views.apply_for_formation, name='apply_formation'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:application_id>/', views.application_detail, name='application_detail'),
    path('application/<int:application_id>/withdraw/', views.withdraw_application, name='withdraw_application'),
    
    # Admin-specific URLs
    path('admin/dashboard/', views.admin_formations_dashboard, name='admin_dashboard'),
    path('admin/list/', views.admin_formations_list, name='admin_list'),
    path('admin/sessions/', views.admin_sessions_list, name='admin_sessions_list'),
    path('admin/evaluations/', views.admin_evaluations_list, name='admin_evaluations_list'),
    path('admin/attendance/', views.admin_attendance_list, name='admin_attendance_list'),
    path('admin/create/', views.admin_formation_create, name='admin_formation_create'),
    path('admin/<int:formation_id>/', views.admin_formation_detail, name='admin_formation_detail'),
    path('admin/<int:formation_id>/edit/', views.admin_formation_edit, name='admin_formation_edit'),
    path('admin/<int:formation_id>/delete/', views.admin_formation_delete, name='admin_formation_delete'),
    path('admin/assign-trainer/', views.admin_assign_trainer, name='admin_assign_trainer'),
    path('admin/<int:formation_id>/status-update/', views.admin_formation_status_update, name='admin_formation_status_update'),
    path('admin/bulk-status-update/', views.admin_formation_bulk_status_update, name='admin_formation_bulk_status_update'),
    
    # Admin application management
    path('admin/applications/', views.admin_applications_list, name='admin_applications_list'),
    path('admin/application/<int:application_id>/review/', views.admin_application_review, name='admin_application_review'),
    
    # Task management URLs
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/dashboard/', views.task_dashboard, name='task_dashboard'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/toggle-status/', views.task_toggle_status, name='task_toggle_status'),
]
