from django.db import models
from users.models import Apprenant
from courses.models import Cours, RessourceCours

class Quiz(models.Model):
    """Quiz resource, linked to a course or resource."""
    titre = models.CharField(max_length=200)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='quizzes')
    ressource = models.ForeignKey(RessourceCours, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes')
    total_questions = models.PositiveIntegerField(default=0)
    seuil_reussite = models.PositiveIntegerField(default=60, help_text="Score minimum (%) pour réussir")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} ({self.cours.titre})"

class QuizResult(models.Model):
    """Result of a quiz for an apprenant."""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results')
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE, related_name='quiz_results')
    score = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    date_passage = models.DateTimeField(auto_now_add=True)
    passed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('quiz', 'apprenant')

    def __str__(self):
        return f"{self.apprenant} - {self.quiz.titre}: {self.score}/{self.total}"

class Certification(models.Model):
    """Certification for a course or set of quizzes."""
    titre = models.CharField(max_length=200)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='certifications')
    quizzes_requis = models.ManyToManyField(Quiz, blank=True)
    seuil_completion = models.PositiveIntegerField(default=80, help_text="% de progression requis pour certification")
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} ({self.cours.titre})"

class CertificationProgress(models.Model):
    """Track apprenant's progress toward certification."""
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE, related_name='progresses')
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE, related_name='certification_progresses')
    date_started = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('certification', 'apprenant')

    def __str__(self):
        return f"{self.apprenant} - {self.certification.titre}"

class LearningGoal(models.Model):
    """Weekly or monthly learning goal for an apprenant."""
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE, related_name='learning_goals')
    periode = models.CharField(max_length=10, choices=[('week', 'Semaine'), ('month', 'Mois')], default='week')
    objectif_lecons = models.PositiveIntegerField(default=3)
    lecons_terminees = models.PositiveIntegerField(default=0)
    date_debut = models.DateField()
    date_fin = models.DateField()
    atteint = models.BooleanField(default=False)

    def __str__(self):
        return f"Goal {self.apprenant} {self.periode} {self.date_debut} - {self.date_fin}"
