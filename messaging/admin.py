from django.contrib import admin
from .models import Message, GroupeChat, MessageGroupe, FilDiscussion, ReponseDiscussion


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sujet', 'expediteur', 'destinataire', 'lu', 'important', 'date_envoi')
    list_filter = ('lu', 'important', 'archive', 'date_envoi')
    search_fields = ('sujet', 'expediteur__email', 'destinataire__email')
    date_hierarchy = 'date_envoi'


@admin.register(GroupeChat)
class GroupeChatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'createur', 'formation', 'prive', 'actif', 'date_creation')
    list_filter = ('prive', 'actif', 'date_creation')
    search_fields = ('nom', 'createur__email', 'formation__titre')


@admin.register(MessageGroupe)
class MessageGroupeAdmin(admin.ModelAdmin):
    list_display = ('groupe', 'auteur', 'date_envoi', 'modifie')
    list_filter = ('modifie', 'date_envoi')
    search_fields = ('groupe__nom', 'auteur__email')
    date_hierarchy = 'date_envoi'


@admin.register(FilDiscussion)
class FilDiscussionAdmin(admin.ModelAdmin):
    list_display = ('titre', 'formation', 'auteur', 'epingle', 'ferme', 'nb_reponses', 'date_creation')
    list_filter = ('epingle', 'ferme', 'date_creation')
    search_fields = ('titre', 'formation__titre', 'auteur__email')
    
    def nb_reponses(self, obj):
        return obj.nb_reponses
    nb_reponses.short_description = 'Réponses'


@admin.register(ReponseDiscussion)
class ReponseDiscussionAdmin(admin.ModelAdmin):
    list_display = ('discussion', 'auteur', 'date_creation', 'modifie')
    list_filter = ('modifie', 'date_creation')
    search_fields = ('discussion__titre', 'auteur__email')
