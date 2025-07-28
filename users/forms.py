from django import forms
from .models import Reclamation

class ReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        fields = ['sujet', 'description', 'priorite']
        widgets = {
            'sujet': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet de la réclamation'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Décrivez votre problème'}),
            'priorite': forms.Select(attrs={'class': 'form-control'}),
        }
