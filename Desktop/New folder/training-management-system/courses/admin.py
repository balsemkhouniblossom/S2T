from django.contrib import admin
from .models import Cours, RessourceCours, ProgressionCours, CommentaireCours


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('titre', 'formateur', 'niveau', 'prix', 'publie', 'nombre_inscrits', 'date_creation')
    list_filter = ('niveau', 'publie', 'gratuit', 'date_creation')
    search_fields = ('titre', 'formateur__utilisateur__nom', 'categorie')
    date_hierarchy = 'date_creation'
    
    def nombre_inscrits(self, obj):
        return obj.nombre_inscrits
    nombre_inscrits.short_description = 'Inscrits'


@admin.register(RessourceCours)
class RessourceCoursAdmin(admin.ModelAdmin):
    list_display = ('titre', 'cours', 'type_ressource', 'obligatoire', 'ordre')
    list_filter = ('type_ressource', 'obligatoire')
    search_fields = ('titre', 'cours__titre')


@admin.register(ProgressionCours)
class ProgressionCoursAdmin(admin.ModelAdmin):
    list_display = ('cours', 'apprenant', 'progression_pourcentage', 'termine', 'derniere_activite')
    list_filter = ('termine', 'date_inscription')
    search_fields = ('cours__titre', 'apprenant__utilisateur__nom')


@admin.register(CommentaireCours)
class CommentaireCoursAdmin(admin.ModelAdmin):
    list_display = ('cours', 'apprenant', 'note', 'approuve', 'date_creation')
    list_filter = ('note', 'approuve', 'date_creation')
    search_fields = ('cours__titre', 'apprenant__utilisateur__nom')
