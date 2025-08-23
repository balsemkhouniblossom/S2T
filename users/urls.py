

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # Password reset URLs
    path('password_reset/', views.CustomPasswordResetView.as_view(
        success_url='/users/password_reset_done/',
        email_template_name='users/password_reset_email.html'
    ), name='password_reset'),
    path('password_reset_done/', views.custom_password_reset_done, name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(
        success_url='/users/password_reset_complete/'
    ), name='password_reset_confirm'),
    path('password_reset_complete/', views.custom_password_reset_complete, name='password_reset_complete'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/<int:user_id>/activate/', views.admin_user_activate, name='admin_user_activate'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('reclamations/nouvelle/', views.submit_reclamation, name='reclamation_submit'),
    path('reclamations/', views.reclamation_list, name='reclamation_list'),
    path('reclamations/<int:reclamation_id>/', views.reclamation_detail, name='reclamation_detail'),
    path('details-users/', views.user_details_view, name='user_details'),
]
