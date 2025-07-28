from django import forms
from django.contrib.auth import get_user_model
from .models import Formation, Salle, Planning, Evaluation, TrainerApplication, Task
from payments.models import Organisation
from users.models import Formateur

User = get_user_model()

class AdminFormationForm(forms.ModelForm):
    """Enhanced formation form for administrators"""
    
    class Meta:
        model = Formation
        fields = [
            'titre', 'description', 'objectifs', 'duree_heures', 'niveau', 
            'prix', 'formateur', 'participants_max', 'prerequisites', 
            'date_debut', 'date_fin', 'statut'
        ]
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la formation'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée de la formation'
            }),
            'objectifs': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Objectifs pédagogiques de la formation'
            }),
            'duree_heures': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'placeholder': 'Durée en heures'
            }),
            'niveau': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'placeholder': 'Prix en euros'
            }),
            'formateur': forms.Select(attrs={
                'class': 'form-control'
            }),
            'participants_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100,
                'placeholder': 'Nombre maximum de participants'
            }),
            'prerequisites': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Prérequis nécessaires (optionnel)'
            }),
            'date_debut': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'date_fin': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate formateur choices
        self.fields['formateur'].queryset = Formateur.objects.select_related('utilisateur').all()
        self.fields['formateur'].empty_label = "Sélectionnez un formateur"
        
        # Add help text
        self.fields['date_debut'].help_text = "Date et heure de début de la formation"
        self.fields['date_fin'].help_text = "Date et heure de fin de la formation"
        self.fields['statut'].help_text = "Statut de la formation"

class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = ['titre', 'description', 'date_debut', 'date_fin', 'duree_heures', 
                 'prix', 'niveau', 'prerequisites', 'formateur']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de la formation'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée de la formation'
            }),
            'date_debut': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'date_fin': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duree_heures': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'prix': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0
            }),
            'niveau': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prerequisites': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Prérequis nécessaires'
            }),
            'formateur': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only formateurs
        try:
            self.fields['formateur'].queryset = Formateur.objects.all()
        except ImportError:
            pass

class PlanningForm(forms.ModelForm):
    class Meta:
        model = Planning
        fields = ['formation', 'salle', 'date_session', 'duree_session', 'sujet', 'description']
        widgets = {
            'formation': forms.Select(attrs={'class': 'form-control'}),
            'salle': forms.Select(attrs={'class': 'form-control'}),
            'date_session': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duree_session': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'max': 480,
                'step': 15,
                'placeholder': 'Durée en minutes'
            }),
            'sujet': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sujet de la session'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description détaillée (optionnel)'
            })
        }

class EvaluationForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['note_contenu', 'note_formateur', 'note_organisation', 'note_globale', 'commentaire', 'recommande']
        widgets = {
            'note_contenu': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1
            }),
            'note_formateur': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1
            }),
            'note_organisation': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1
            }),
            'note_globale': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Votre avis sur la formation...'
            }),
            'recommande': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class FormationSearchForm(forms.Form):
    q = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher une formation...'
        })
    )
    niveau = forms.ChoiceField(
        choices=[('', 'Tous les niveaux')] + [
            ('debutant', 'Débutant'),
            ('intermediaire', 'Intermédiaire'),
            ('avance', 'Avancé'),
            ('expert', 'Expert'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    prix_min = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prix minimum'
        })
    )
    prix_max = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prix maximum'
        })
    )

class SalleForm(forms.ModelForm):
    class Meta:
        model = Salle
        fields = ['nom', 'capacite', 'equipements', 'localisation']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la salle'
            }),
            'capacite': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'equipements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Équipements disponibles'
            }),
            'localisation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Adresse de la salle'
            })
        }


class TrainerApplicationForm(forms.ModelForm):
    """Form for trainers to apply for formations"""
    
    class Meta:
        model = TrainerApplication
        fields = [
            'motivation', 'experience_pertinente', 'tarif_propose', 
            'disponibilite', 'message'
        ]
        widgets = {
            'motivation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Pourquoi souhaitez-vous animer cette formation? Quelles sont vos motivations?',
                'required': True
            }),
            'experience_pertinente': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Décrivez votre expérience pertinente pour cette formation (formations similaires, expertise dans le domaine, etc.)',
                'required': True
            }),
            'tarif_propose': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': 0,
                'placeholder': 'Votre tarif horaire proposé (optionnel)'
            }),
            'disponibilite': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Indiquez vos créneaux de disponibilité pour cette formation',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Message libre ou informations complémentaires (optionnel)'
            })
        }
        labels = {
            'motivation': 'Motivation *',
            'experience_pertinente': 'Expérience pertinente *',
            'tarif_propose': 'Tarif horaire proposé (€)',
            'disponibilite': 'Disponibilité *',
            'message': 'Message complémentaire'
        }
        help_texts = {
            'motivation': 'Expliquez pourquoi cette formation vous intéresse et ce que vous pourriez apporter.',
            'experience_pertinente': 'Mettez en avant votre expertise et vos expériences en lien avec le sujet.',
            'tarif_propose': 'Laissez vide si vous préférez discuter du tarif ultérieurement.',
            'disponibilite': 'Précisez vos créneaux libres en tenant compte des dates de la formation.',
            'message': 'Ajoutez toute information que vous jugez utile pour votre candidature.'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required
        self.fields['motivation'].required = True
        self.fields['experience_pertinente'].required = True
        self.fields['disponibilite'].required = True


class TrainerApplicationReviewForm(forms.ModelForm):
    """Form for admins to review trainer applications"""
    
    class Meta:
        model = TrainerApplication
        fields = ['statut', 'commentaire_admin']
        widgets = {
            'statut': forms.Select(attrs={
                'class': 'form-control'
            }),
            'commentaire_admin': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Commentaire pour le formateur (optionnel)'
            })
        }
        labels = {
            'statut': 'Décision',
            'commentaire_admin': 'Commentaire pour le formateur'
        }


class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    
    class Meta:
        model = Task
        fields = [
            'titre', 'description', 'priorite', 'statut', 'categorie',
            'date_echeance', 'formation_liee', 'notes', 'fichiers_attaches'
        ]
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le titre de la tâche...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description détaillée de la tâche...'
            }),
            'priorite': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'date_echeance': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'formation_liee': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes additionnelles...'
            }),
            'fichiers_attaches': forms.FileInput(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter formations based on user type
        if user:
            try:
                # If user is a formateur
                if hasattr(user, 'formateur'):
                    formateur = user.formateur
                    self.fields['formation_liee'].queryset = Formation.objects.filter(formateur=formateur)
                elif hasattr(user, 'apprenant'):
                    # If user is an apprenant
                    apprenant = user.apprenant
                    # Get formations where apprenant is enrolled
                    self.fields['formation_liee'].queryset = Formation.objects.filter(
                        participants=apprenant
                    )
                else:
                    # Default queryset for other user types
                    self.fields['formation_liee'].queryset = Formation.objects.none()
            except:
                self.fields['formation_liee'].queryset = Formation.objects.none()


class TaskFilterForm(forms.Form):
    """Form for filtering tasks"""
    
    STATUS_CHOICES = [('', 'Tous les statuts')] + Task.STATUS_CHOICES
    PRIORITY_CHOICES = [('', 'Toutes les priorités')] + Task.PRIORITY_CHOICES
    CATEGORY_CHOICES = [('', 'Toutes les catégories')] + Task.CATEGORY_CHOICES
    
    statut = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priorite = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    categorie = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        required=False,
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
    recherche = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher dans les tâches...'
        })
    )

## OrganisationEnrollmentForm is disabled because OrganisationEnrollment model does not exist.
## Uncomment and implement the correct model to enable this form.
