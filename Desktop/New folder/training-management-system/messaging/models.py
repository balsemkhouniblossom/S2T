from django.db import models
from django.utils import timezone
from users.models import Utilisateur
from formations.models import Formation


class Message(models.Model):
    """Private messages"""
    expediteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='messages_recus')
    sujet = models.CharField(max_length=200)
    contenu = models.TextField()
    fichier_joint = models.FileField(upload_to='messages/', blank=True, null=True)
    date_envoi = models.DateTimeField(default=timezone.now)
    lu = models.BooleanField(default=False)
    date_lecture = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f"De {self.expediteur} à {self.destinataire}: {self.sujet}"


class GroupeChat(models.Model):
    """Group chats"""
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    createur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='groupes_crees')
    membres = models.ManyToManyField(Utilisateur, related_name='groupes_membre')
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, null=True, blank=True)
    prive = models.BooleanField(default=False)
    date_creation = models.DateTimeField(default=timezone.now)
    actif = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Groupe de Chat'
        verbose_name_plural = 'Groupes de Chat'
        ordering = ['-date_creation']
    
    def __str__(self):
        return self.nom


class MessageGroupe(models.Model):
    """Group messages"""
    groupe = models.ForeignKey(GroupeChat, on_delete=models.CASCADE, related_name='messages')
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    contenu = models.TextField()
    fichier_joint = models.FileField(upload_to='groupes/', blank=True, null=True)
    date_envoi = models.DateTimeField(default=timezone.now)
    modifie = models.BooleanField(default=False)
    date_modification = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Message de Groupe'
        verbose_name_plural = 'Messages de Groupe'
        ordering = ['date_envoi']
    
    def __str__(self):
        return f"{self.auteur} dans {self.groupe.nom}"


class FilDiscussion(models.Model):
    """Discussion threads"""
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, related_name='discussions')
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    epingle = models.BooleanField(default=False)
    ferme = models.BooleanField(default=False)
    date_creation = models.DateTimeField(default=timezone.now)
    derniere_reponse = models.DateTimeField(null=True, blank=True)
    nb_vues = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Fil de Discussion'
        verbose_name_plural = 'Fils de Discussion'
        ordering = ['-epingle', '-derniere_reponse']
    
    def __str__(self):
        return self.titre
    
    @property
    def nb_reponses(self):
        return self.reponses.count()


class ReponseDiscussion(models.Model):
    """Discussion replies"""
    discussion = models.ForeignKey(FilDiscussion, on_delete=models.CASCADE, related_name='reponses')
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    contenu = models.TextField()
    fichier_joint = models.FileField(upload_to='discussions/', blank=True, null=True)
    date_creation = models.DateTimeField(default=timezone.now)
    modifie = models.BooleanField(default=False)
    date_modification = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Réponse de Discussion'
        verbose_name_plural = 'Réponses de Discussion'
        ordering = ['date_creation']
    
    def __str__(self):
        return f"Réponse à {self.discussion.titre} par {self.auteur}"
