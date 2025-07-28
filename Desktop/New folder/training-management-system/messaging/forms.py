from django import forms
from django.contrib.auth import get_user_model
from .models import Message, GroupeChat, MessageGroupe, FilDiscussion, ReponseDiscussion

User = get_user_model()

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['destinataire', 'sujet', 'contenu']
        widgets = {
            'destinataire': forms.Select(attrs={
                'class': 'form-control'
            }),
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sujet du message'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Votre message...'
            })
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Exclude the current user from destinataire choices
            self.fields['destinataire'].queryset = User.objects.exclude(id=user.id)

class GroupeChatForm(forms.ModelForm):
    membres = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = GroupeChat
        fields = ['nom', 'description', 'membres']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du groupe'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du groupe'
            })
        }

class MessageGroupeForm(forms.ModelForm):
    class Meta:
        model = MessageGroupe
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Votre message...'
            })
        }

class FilDiscussionForm(forms.ModelForm):
    class Meta:
        model = FilDiscussion
        fields = ['titre', 'contenu', 'categorie']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la discussion'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Contenu de la discussion...'
            }),
            'categorie': forms.Select(attrs={
                'class': 'form-control'
            })
        }

class ReponseDiscussionForm(forms.ModelForm):
    class Meta:
        model = ReponseDiscussion
        fields = ['contenu']
        widgets = {
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Votre réponse...'
            })
        }

class MessageSearchForm(forms.Form):
    q = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher dans les messages...'
        })
    )
    expediteur = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="Tous les expéditeurs",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
