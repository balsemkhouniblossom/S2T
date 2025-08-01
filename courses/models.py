from django.db import models
from django.utils import timezone
from users.models import Formateur, Apprenant


class Cours(models.Model):
    """Individual courses"""
    NIVEAU_CHOICES = [
        ('debutant', 'Débutant'),
        ('intermediaire', 'Intermédiaire'),
        ('avance', 'Avancé'),
        ('expert', 'Expert'),
    ]
    titre = models.CharField(max_length=200)
    description = models.TextField()
    contenu = models.TextField()
    formateur = models.ForeignKey(Formateur, on_delete=models.CASCADE)
    duree_minutes = models.PositiveIntegerField()
    niveau = models.CharField(max_length=50, choices=NIVEAU_CHOICES)
    categorie = models.CharField(max_length=100)
    mots_cles = models.CharField(max_length=500, help_text="Mots-clés séparés par des virgules")
    image_couverture = models.ImageField(upload_to='cours/', blank=True, null=True)
    prix = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    gratuit = models.BooleanField(default=False)
    publie = models.BooleanField(default=False)
    date_creation = models.DateTimeField(default=timezone.now)
    date_publication = models.DateTimeField(null=True, blank=True)
    nb_vues = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'
        ordering = ['-date_creation']
    
    def __str__(self):
        return self.titre
    
    @property
    def nombre_inscrits(self):
        return self.progressions.count()
    
    @property
    def note_moyenne(self):
        commentaires = self.commentaires.all()
        if commentaires:
            return sum(c.note for c in commentaires) / len(commentaires)
        return 0


class RessourceCours(models.Model):
    """Course resources"""
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='ressources')
    titre = models.CharField(max_length=200)
    type_ressource = models.CharField(max_length=50, choices=[
        ('video', 'Vidéo'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('lien', 'Lien externe'),
        ('exercice', 'Exercice'),
        ('quiz', 'Quiz'),
    ])
    fichier = models.FileField(upload_to='cours/ressources/', blank=True, null=True)
    lien_externe = models.URLField(blank=True)
    description = models.TextField(blank=True)
    ordre = models.PositiveIntegerField(default=0)
    obligatoire = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Ressource de Cours'
        verbose_name_plural = 'Ressources de Cours'
        ordering = ['ordre']
    
    def __str__(self):
        return f"{self.cours.titre} - {self.titre}"


class ProgressionCours(models.Model):
    """Learning progress"""
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='progressions')
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    date_inscription = models.DateTimeField(default=timezone.now)
    progression_pourcentage = models.PositiveIntegerField(default=0)
    temps_passe_minutes = models.PositiveIntegerField(default=0)
    derniere_activite = models.DateTimeField(auto_now=True)
    termine = models.BooleanField(default=False)
    date_completion = models.DateTimeField(null=True, blank=True)
    ressources_completees = models.ManyToManyField(RessourceCours, blank=True)
    
    class Meta:
        verbose_name = 'Progression de Cours'
        verbose_name_plural = 'Progressions de Cours'
        unique_together = ['cours', 'apprenant']
    
    def __str__(self):
        return f"{self.apprenant} - {self.cours.titre} ({self.progression_pourcentage}%)"


class CommentaireCours(models.Model):
    """Course comments"""
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='commentaires')
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    note = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    commentaire = models.TextField()
    date_creation = models.DateTimeField(default=timezone.now)
    approuve = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Commentaire de Cours'
        verbose_name_plural = 'Commentaires de Cours'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"Commentaire sur {self.cours.titre} par {self.apprenant}"
