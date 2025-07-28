from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/<int:user_id>/activate/', views.admin_user_activate, name='admin_user_activate'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('update_confirmation/<int:user_id>/', views.update_confirmation, name='update_confirmation'),
    path('reclamations/nouvelle/', views.submit_reclamation, name='reclamation_submit'),
    path('reclamations/', views.reclamation_list, name='reclamation_list'),
    path('reclamations/<int:reclamation_id>/', views.reclamation_detail, name='reclamation_detail'),
]
