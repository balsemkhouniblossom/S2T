from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Utilisateur(AbstractUser):
    """Base user model with email authentication"""
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    photo_profil = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_creation = models.DateTimeField(default=timezone.now)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    derniere_deconnexion = models.DateTimeField(null=True, blank=True)
    confirmation = models.CharField(max_length=20, default='En cours')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nom', 'prenom']
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"



# --- Structured models for certifications and competences ---
class Competence(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.nom

class Certification(models.Model):
    nom = models.CharField(max_length=200)
    organisme = models.CharField(max_length=200, blank=True)
    date_obtention = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.nom

class Formateur(models.Model):
    """Trainer model extending base user"""
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)
    parcours = models.TextField(blank=True, help_text="Expérience professionnelle, formation, licences et certifications")
    competences = models.ManyToManyField(Competence, blank=True, related_name='formateurs')
    certifications = models.ManyToManyField(Certification, blank=True, related_name='formateurs')
    experience = models.PositiveIntegerField(default=0, help_text="Années d'expérience")
    description = models.TextField(blank=True)
    tarif_horaire = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    disponible = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Formateur'
        verbose_name_plural = 'Formateurs'

    def __str__(self):
        return f"Formateur: {self.utilisateur}"


class Apprenant(models.Model):
    """Learner model extending base user"""
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    entreprise = models.CharField(max_length=200, blank=True)
    poste = models.CharField(max_length=100, blank=True)
    niveau_etude = models.CharField(max_length=100, blank=True)
    objectifs = models.TextField(blank=True)
    date_inscription = models.DateTimeField(default=timezone.now)
    organisation = models.ForeignKey('payments.Organisation', null=True, blank=True, on_delete=models.SET_NULL, related_name='apprenants')
    
    class Meta:
        verbose_name = 'Apprenant'
        verbose_name_plural = 'Apprenants'
    
    def __str__(self):
        return f"Apprenant: {self.utilisateur}"


class Administrateur(models.Model):
    """Administrator model extending base user"""
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    niveau_acces = models.CharField(max_length=50, choices=[
        ('super', 'Super Administrateur'),
        ('admin', 'Administrateur'),
        ('moderateur', 'Modérateur'),
    ], default='admin')
    departement = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Administrateur'
        verbose_name_plural = 'Administrateurs'
    
    def __str__(self):
        return f"Admin: {self.utilisateur}"


class Notification(models.Model):
    """System notifications"""
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    message = models.TextField()
    type_notification = models.CharField(max_length=50, choices=[
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('success', 'Succès'),
        ('error', 'Erreur'),
    ])
    lu = models.BooleanField(default=False)
    date_creation = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.titre} - {self.utilisateur}"


class Reclamation(models.Model):
    """User complaints/issues"""
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    sujet = models.CharField(max_length=200)
    description = models.TextField()
    statut = models.CharField(max_length=50, choices=[
        ('ouverte', 'Ouverte'),
        ('en_cours', 'En cours'),
        ('resolue', 'Résolue'),
        ('fermee', 'Fermée'),
    ], default='ouverte')
    priorite = models.CharField(max_length=20, choices=[
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ], default='normale')
    date_creation = models.DateTimeField(default=timezone.now)
    date_resolution = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Réclamation'
        verbose_name_plural = 'Réclamations'
        ordering = ['-date_creation']
    
    def __str__(self):
        return f"{self.sujet} - {self.utilisateur}"
