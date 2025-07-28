from django.urls import path
from . import views
from .api import apprenant_organisation_api

app_name = 'payments'

urlpatterns = [
    path('admin/', views.admin_list, name='admin_list'),
    path('dashboard/', views.payments_dashboard, name='dashboard'),
    path('sponsorship/new/', views.create_sponsorship, name='create_sponsorship'),
    path('paiement/new/', views.create_paiement, name='create_paiement'),
    path('api/apprenant/<int:apprenant_id>/organisation/', apprenant_organisation_api, name='apprenant_organisation_api'),
    path('enrollment/<int:inscription_id>/activate/', views.activate_enrollment, name='activate_enrollment'),
]
