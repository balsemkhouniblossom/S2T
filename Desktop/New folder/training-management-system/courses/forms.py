from django import forms
from django.contrib.auth import get_user_model
from .models import Cours, RessourceCours, CommentaireCours

User = get_user_model()

class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['titre', 'description', 'contenu', 'duree_minutes', 'niveau', 
                 'prerequis', 'video_url', 'image', 'formateur']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du cours'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du cours'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Contenu détaillé du cours'
            }),
            'duree_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'niveau': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prerequis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Prérequis nécessaires'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL de la vidéo (optionnel)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'formateur': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only formateurs
        try:
            from users.models import Formateur
            self.fields['formateur'].queryset = Formateur.objects.all()
        except ImportError:
            pass

class RessourceCoursForm(forms.ModelForm):
    class Meta:
        model = RessourceCours
        fields = ['titre', 'description', 'fichier', 'url_externe', 'type_ressource']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la ressource'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la ressource'
            }),
            'fichier': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'url_externe': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL externe (optionnel)'
            }),
            'type_ressource': forms.Select(attrs={
                'class': 'form-control'
            })
        }

class CommentaireCoursForm(forms.ModelForm):
    class Meta:
        model = CommentaireCours
        fields = ['commentaire', 'note']
        widgets = {
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Votre commentaire sur le cours...'
            }),
            'note': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 0.5
            })
        }

class CourseSearchForm(forms.Form):
    q = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher un cours...'
        })
    )
    niveau = forms.ChoiceField(
        choices=[('', 'Tous les niveaux')] + Cours.NIVEAU_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    duree_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Durée minimum (minutes)'
        })
    )
    duree_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Durée maximum (minutes)'
        })
    )
    formateur = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Tous les formateurs",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only formateurs
        try:
            from users.models import Formateur
            self.fields['formateur'].queryset = Formateur.objects.all()
        except ImportError:
            pass
