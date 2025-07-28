from django.db import models
from users.models import Utilisateur

class ForumQuestion(models.Model):
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

class ForumComment(models.Model):
    question = models.ForeignKey(ForumQuestion, related_name='commentaires', on_delete=models.CASCADE)
    auteur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire par {self.auteur.nom} sur {self.question.titre}"
