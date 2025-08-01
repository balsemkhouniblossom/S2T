from django.contrib import admin
from .quiz_models import Quiz, QuizResult, Certification, CertificationProgress, LearningGoal

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('titre', 'cours', 'total_questions', 'seuil_reussite', 'date_creation')
    search_fields = ('titre', 'cours__titre')
    list_filter = ('cours',)

@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'apprenant', 'score', 'total', 'passed', 'date_passage')
    search_fields = ('quiz__titre', 'apprenant__utilisateur__nom')
    list_filter = ('quiz', 'passed')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'cours', 'seuil_completion', 'date_creation')
    search_fields = ('titre', 'cours__titre')
    list_filter = ('cours',)

@admin.register(CertificationProgress)
class CertificationProgressAdmin(admin.ModelAdmin):
    list_display = ('certification', 'apprenant', 'completed', 'date_started', 'date_completed')
    search_fields = ('certification__titre', 'apprenant__utilisateur__nom')
    list_filter = ('certification', 'completed')

@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ('apprenant', 'periode', 'objectif_lecons', 'lecons_terminees', 'date_debut', 'date_fin', 'atteint')
    search_fields = ('apprenant__utilisateur__nom',)
    list_filter = ('periode', 'atteint')
