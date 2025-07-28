from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Formateur, Apprenant, Administrateur, Notification, Reclamation


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('email', 'prenom', 'nom', 'is_active', 'date_creation')
    list_filter = ('is_active', 'is_staff', 'date_creation')
    search_fields = ('email', 'prenom', 'nom')
    ordering = ('email',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'telephone', 'adresse', 'date_naissance', 'photo_profil')
        }),
    )


@admin.register(Formateur)
class FormateurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'experience', 'tarif_horaire', 'disponible')
    list_filter = ('disponible', 'experience')
    search_fields = ('utilisateur__email', 'utilisateur__nom', 'competences')


@admin.register(Apprenant)
class ApprenantAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'entreprise', 'poste', 'date_inscription')
    list_filter = ('date_inscription', 'entreprise')
    search_fields = ('utilisateur__email', 'utilisateur__nom', 'entreprise')


@admin.register(Administrateur)
class AdministrateurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'niveau_acces', 'departement')
    list_filter = ('niveau_acces',)
    search_fields = ('utilisateur__email', 'utilisateur__nom')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'utilisateur', 'type_notification', 'lu', 'date_creation')
    list_filter = ('type_notification', 'lu', 'date_creation')
    search_fields = ('titre', 'utilisateur__email')


@admin.register(Reclamation)
class ReclamationAdmin(admin.ModelAdmin):
    list_display = ('sujet', 'utilisateur', 'statut', 'priorite', 'date_creation')
    list_filter = ('statut', 'priorite', 'date_creation')
    search_fields = ('sujet', 'utilisateur__email')
