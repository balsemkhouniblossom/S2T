
from django.db import models
from django.utils import timezone

class Inscription(models.Model):
    apprenant = models.ForeignKey('users.Apprenant', on_delete=models.CASCADE, related_name='inscriptions')
    formation = models.ForeignKey('Formation', on_delete=models.CASCADE, related_name='inscriptions')
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('active', 'Active'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ], default='en_attente')
    date_inscription = models.DateTimeField(default=timezone.now)
    date_activation = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        unique_together = ('apprenant', 'formation')

    def __str__(self):
        return f"{self.apprenant} - {self.formation} [{self.statut}]"

    def activate(self):
        self.statut = 'active'
        self.date_activation = timezone.now()
        self.save()

from django.db import models
from django.utils import timezone
from users.models import Utilisateur, Formateur, Apprenant

# ...existing Organisation and OrganisationEnrollment models here...


class Salle(models.Model):
    """Training rooms"""
    nom = models.CharField(max_length=100)
    capacite = models.PositiveIntegerField()
    localisation = models.CharField(max_length=200)
    equipements = models.TextField(blank=True, help_text="Équipements disponibles")
    disponible = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Salle'
        verbose_name_plural = 'Salles'
    
    def __str__(self):
        return f"{self.nom} (Capacité: {self.capacite})"


class Formation(models.Model):
    """Training formations"""
    titre = models.CharField(max_length=200)
    description = models.TextField()
    objectifs = models.TextField()
    duree_heures = models.PositiveIntegerField(help_text="Durée en heures")
    niveau = models.CharField(max_length=50, choices=[
        ('debutant', 'Débutant'),
        ('intermediaire', 'Intermédiaire'),
        ('avance', 'Avancé'),
        ('expert', 'Expert'),
    ])
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    formateur = models.ForeignKey(Formateur, on_delete=models.CASCADE, null=True, blank=True)
    participants_max = models.PositiveIntegerField(default=20)
    prerequisites = models.TextField(blank=True)
    applications_ouvertes = models.BooleanField(default=False, help_text="Permet aux formateurs de candidater")
    date_limite_candidature = models.DateTimeField(null=True, blank=True, help_text="Date limite pour candidater")
    statut = models.CharField(max_length=50, choices=[
        ('brouillon', 'Brouillon'),
        ('proposition', 'Proposition (candidatures ouvertes)'),
        ('publiee', 'Publiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ], default='brouillon')
    date_creation = models.DateTimeField(default=timezone.now)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    participants = models.ManyToManyField(Apprenant, blank=True, related_name='formations_inscrites')
    cours = models.ManyToManyField('courses.Cours', blank=True, related_name='formations')
    
    class Meta:
        verbose_name = 'Formation'
        verbose_name_plural = 'Formations'
        ordering = ['-date_creation']
    
    def __str__(self):
        return self.titre
    
    @property
    def participants_inscrits(self):
        return self.participants.count()
    
    @property
    def places_restantes(self):
        return self.participants_max - self.participants_inscrits
    
    @property
    def is_open_for_applications(self):
        """Check if this formation accepts trainer applications"""
        if not self.applications_ouvertes:
            return False
        if self.formateur is not None:  # Already has a trainer
            return False
        if self.date_limite_candidature and timezone.now() > self.date_limite_candidature:
            return False
        return self.statut == 'proposition'
    
    @property
    def applications_count(self):
        """Count of trainer applications"""
        return self.trainer_applications.count()
    
    @property
    def pending_applications_count(self):
        """Count of pending trainer applications"""
        return self.trainer_applications.filter(statut='en_attente').count()


class Planning(models.Model):
    """Session scheduling"""
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='sessions')
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    date_session = models.DateTimeField()
    duree_session = models.PositiveIntegerField(help_text="Durée en minutes")
    sujet = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    code_presence = models.CharField(max_length=10, blank=True)
    
    class Meta:
        verbose_name = 'Planning'
        verbose_name_plural = 'Plannings'
        ordering = ['date_session']
    
    def __str__(self):
        return f"{self.formation.titre} - {self.date_session.strftime('%d/%m/%Y %H:%M')}"


class Presence(models.Model):
    """Attendance tracking"""
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)
    heure_arrivee = models.DateTimeField(null=True, blank=True)
    heure_depart = models.DateTimeField(null=True, blank=True)
    commentaire = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Présence'
        verbose_name_plural = 'Présences'
        unique_together = ['planning', 'apprenant']
    
    def __str__(self):
        return f"{self.apprenant} - {self.planning}"


class Evaluation(models.Model):
    """Formation evaluations"""
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='evaluations')
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    note_contenu = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    note_formateur = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    note_organisation = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    note_globale = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    commentaire = models.TextField(blank=True)
    recommande = models.BooleanField(default=True)
    date_evaluation = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Évaluation'
        verbose_name_plural = 'Évaluations'
        unique_together = ['formation', 'apprenant']
    
    def __str__(self):
        return f"Évaluation: {self.formation.titre} par {self.apprenant}"


class Attestation(models.Model):
    """Completion certificates"""
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    numero_attestation = models.CharField(max_length=50, unique=True)
    date_emission = models.DateTimeField(default=timezone.now)
    note_obtenue = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    competences_acquises = models.TextField()
    fichier_pdf = models.FileField(upload_to='attestations/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Attestation'
        verbose_name_plural = 'Attestations'
        unique_together = ['formation', 'apprenant']
    
    def __str__(self):
        return f"Attestation {self.numero_attestation} - {self.apprenant}"


class TrainerApplication(models.Model):
    """Trainer applications for proposed formations"""
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='trainer_applications', null=True, blank=True)
    formateur = models.ForeignKey('users.Formateur', on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    message = models.TextField(blank=True, help_text="Message de motivation ou présentation")
    suggested_formation = models.CharField(max_length=255, blank=True, null=True, help_text="Formation suggérée par le candidat")
    motivation = models.TextField(help_text="Pourquoi souhaitez-vous animer cette formation?")
    experience_pertinente = models.TextField(help_text="Expérience pertinente pour cette formation")
    tarif_propose = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Tarif horaire proposé")
    disponibilite = models.TextField(help_text="Créneaux de disponibilité")
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('rejetee', 'Rejetée'),
        ('retiree', 'Retirée'),
    ], default='en_attente')
    date_candidature = models.DateTimeField(default=timezone.now)
    date_reponse = models.DateTimeField(null=True, blank=True)
    commentaire_admin = models.TextField(blank=True, help_text="Commentaire de l'administrateur")
    
    class Meta:
        verbose_name = 'Candidature Formateur'
        verbose_name_plural = 'Candidatures Formateurs'
        unique_together = ['formation', 'formateur']
        ordering = ['-date_candidature']
    
    def __str__(self):
        return f"{self.formateur.utilisateur.get_full_name()} - {self.formation.titre} ({self.statut})"
    
    @property
    def is_pending(self):
        return self.statut == 'en_attente'
    
    @property
    def is_accepted(self):
        return self.statut == 'acceptee'


class Task(models.Model):
    """Task model for To-Do List Management"""
    
    PRIORITY_CHOICES = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Haute'),
        ('urgent', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'À faire'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ]
    
    CATEGORY_CHOICES = [
        ('formation', 'Formation'),
        ('cours', 'Cours'),
        ('evaluation', 'Évaluation'),
        ('personnel', 'Personnel'),
        ('administratif', 'Administratif'),
    ]
    
    # User who created the task (can be formateur or apprenant)
    createur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='tasks_created')
    
    # Task details
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(blank=True, verbose_name="Description")
    priorite = models.CharField(
        max_length=10, 
        choices=PRIORITY_CHOICES, 
        default='medium',
        verbose_name="Priorité"
    )
    statut = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='todo',
        verbose_name="Statut"
    )
    categorie = models.CharField(
        max_length=15,
        choices=CATEGORY_CHOICES,
        default='personnel',
        verbose_name="Catégorie"
    )
    
    # Dates
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    date_echeance = models.DateTimeField(null=True, blank=True, verbose_name="Date d'échéance")
    date_completion = models.DateTimeField(null=True, blank=True, verbose_name="Date de completion")
    
    # Optional relationships
    formation_liee = models.ForeignKey(
        Formation, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        verbose_name="Formation liée"
    )
    
    # Additional fields
    notes = models.TextField(blank=True, verbose_name="Notes")
    fichiers_attaches = models.FileField(
        upload_to='tasks/attachments/', 
        null=True, 
        blank=True,
        verbose_name="Fichiers attachés"
    )
    
    class Meta:
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['createur', 'statut']),
            models.Index(fields=['date_echeance']),
            models.Index(fields=['priorite']),
        ]
    
    def __str__(self):
        return f"{self.titre} - {self.get_statut_display()}"
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.date_echeance and self.statut != 'completed':
            return timezone.now() > self.date_echeance
        return False
    
    @property
    def days_until_due(self):
        """Get days until due date"""
        if self.date_echeance:
            delta = self.date_echeance - timezone.now()
            return delta.days
        return None
    
    def mark_completed(self):
        """Mark task as completed"""
        self.statut = 'completed'
        self.date_completion = timezone.now()
        self.save()
    
    def get_priority_badge_class(self):
        """Get CSS class for priority badge"""
        priority_classes = {
            'low': 'badge-success',
            'medium': 'badge-warning',
            'high': 'badge-danger',
            'urgent': 'badge-dark'
        }
        return priority_classes.get(self.priorite, 'badge-secondary')
    
    def get_status_badge_class(self):
        """Get CSS class for status badge"""
        status_classes = {
            'todo': 'badge-secondary',
            'in_progress': 'badge-primary',
            'completed': 'badge-success',
            'cancelled': 'badge-dark'
        }
        return status_classes.get(self.statut, 'badge-secondary')
