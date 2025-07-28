from django import forms
from .models import SponsoringOrganisation, Paiement, Organisation, Apprenant, Formation

class SponsoringOrganisationForm(forms.ModelForm):
    class Meta:
        model = SponsoringOrganisation
        fields = [
            'organisation', 'apprenant', 'formation',
            'pourcentage_prise_charge', 'montant_prise_charge', 'statut', 'commentaire'
        ]
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class PaiementForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apprenant = self.initial.get('apprenant') or self.data.get('apprenant')
        if apprenant:
            from users.models import Apprenant
            try:
                apprenant_obj = Apprenant.objects.get(pk=apprenant)
                if apprenant_obj.organisation:
                    self.fields['organisation'].initial = apprenant_obj.organisation.pk
            except Apprenant.DoesNotExist:
                pass
    def clean(self):
        cleaned_data = super().clean()
        apprenant = cleaned_data.get('apprenant')
        organisation = cleaned_data.get('organisation')
        if not apprenant and not organisation:
            raise forms.ValidationError("Vous devez spécifier soit un utilisateur (apprenant), soit une organisation comme payeur.")
        # Optionally, to enforce only one, uncomment below:
        # if apprenant and organisation:
        #     raise forms.ValidationError("Un paiement ne peut être associé qu'à un seul payeur à la fois.")
        return cleaned_data
    class Meta:
        model = Paiement
        fields = [
            'formation', 'apprenant', 'organisation', 'montant',
            'mode_paiement', 'statut', 'reference_transaction', 'commentaire'
        ]
        widgets = {
            'mode_paiement': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'commentaire': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
