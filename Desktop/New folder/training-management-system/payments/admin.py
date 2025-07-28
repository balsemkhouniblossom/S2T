from django.contrib import admin
from .models import Organisation, Paiement, Facture, Remise, SponsoringOrganisation


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'secteur_activite', 'contact_principal', 'active', 'date_creation')
    list_filter = ('active', 'secteur_activite', 'date_creation')
    search_fields = ('nom', 'contact_principal', 'email')


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('reference_transaction', 'formation', 'montant', 'mode_paiement', 'statut', 'date_paiement')
    list_filter = ('mode_paiement', 'statut', 'date_paiement')
    search_fields = ('reference_transaction', 'formation__titre')
    date_hierarchy = 'date_paiement'


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('numero_facture', 'montant_ttc', 'statut', 'date_emission', 'date_echeance')
    list_filter = ('statut', 'date_emission')
    search_fields = ('numero_facture', 'paiement__reference_transaction')
    date_hierarchy = 'date_emission'


@admin.register(Remise)
class RemiseAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'type_remise', 'valeur', 'utilisable', 'date_debut', 'date_fin')
    list_filter = ('type_remise', 'active', 'date_debut')
    search_fields = ('code', 'description')
    
    def utilisable(self, obj):
        return obj.utilisable
    utilisable.boolean = True
    utilisable.short_description = 'Utilisable'


@admin.register(SponsoringOrganisation)
class SponsoringOrganisationAdmin(admin.ModelAdmin):
    list_display = ('organisation', 'apprenant', 'formation', 'pourcentage_prise_charge', 'statut', 'date_accord')
    list_filter = ('statut', 'date_accord')
    search_fields = ('organisation__nom', 'apprenant__utilisateur__nom', 'formation__titre')
