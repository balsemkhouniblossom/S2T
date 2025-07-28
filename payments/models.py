from django.db import models
from django.utils import timezone
from users.models import Utilisateur, Apprenant
from formations.models import Formation


class Organisation(models.Model):
    """Companies/organizations"""
    nom = models.CharField(max_length=200)
    secteur_activite = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    site_web = models.URLField(blank=True)
    contact_principal = models.CharField(max_length=100)
    numero_siret = models.CharField(max_length=14, blank=True)
    tva_applicable = models.BooleanField(default=True)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    date_creation = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Organisation'
        verbose_name_plural = 'Organisations'
    
    def __str__(self):
        return self.nom


class Paiement(models.Model):
    @property
    def payer_type(self):
        """Return 'apprenant', 'organisation', or 'mixte' if both are set."""
        if self.apprenant and self.organisation:
            return 'mixte'
        elif self.apprenant:
            return 'apprenant'
        elif self.organisation:
            return 'organisation'
        return None

    @property
    def payer_name(self):
        """Return the name of the payer (apprenant or organisation)."""
        if self.organisation:
            return self.organisation.nom
        elif self.apprenant:
            return self.apprenant.utilisateur.get_full_name()
        return None

    @property
    def payer_email(self):
        """Return the email of the payer (organisation or apprenant)."""
        if self.organisation:
            return self.organisation.email
        elif self.apprenant:
            return self.apprenant.utilisateur.email
        return None

    @classmethod
    def organisation_payments(cls, organisation):
        """Return all payments made by a given organisation."""
        return cls.objects.filter(organisation=organisation)
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.apprenant and not self.organisation:
            raise ValidationError("Un paiement doit être associé à un apprenant ou une organisation.")
        if self.apprenant and self.organisation:
            # Optionally allow both, or raise a warning if you want only one
            pass

    @property
    def payeur(self):
        """Return the payer: apprenant or organisation"""
        return self.apprenant or self.organisation
    """Payment transactions"""
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE, null=True, blank=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, null=True, blank=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=50, choices=[
        ('carte', 'Carte bancaire'),
        ('virement', 'Virement bancaire'),
        ('cheque', 'Chèque'),
        ('especes', 'Espèces'),
        ('paypal', 'PayPal'),
    ])
    statut = models.CharField(max_length=50, choices=[
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('refuse', 'Refusé'),
        ('rembourse', 'Remboursé'),
    ], default='en_attente')
    reference_transaction = models.CharField(max_length=100, unique=True)
    date_paiement = models.DateTimeField(default=timezone.now)
    date_validation = models.DateTimeField(null=True, blank=True)
    commentaire = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']
    
    def __str__(self):
        payeur = self.apprenant or self.organisation
        return f"Paiement {self.reference_transaction} - {payeur}"


class Facture(models.Model):
    """Invoices"""
    numero_facture = models.CharField(max_length=50, unique=True)
    paiement = models.OneToOneField(Paiement, on_delete=models.CASCADE)
    date_emission = models.DateTimeField(default=timezone.now)
    date_echeance = models.DateTimeField()
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=50, choices=[
        ('brouillon', 'Brouillon'),
        ('envoyee', 'Envoyée'),
        ('payee', 'Payée'),
        ('en_retard', 'En retard'),
        ('annulee', 'Annulée'),
    ], default='brouillon')
    fichier_pdf = models.FileField(upload_to='factures/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-date_emission']
    
    def __str__(self):
        return f"Facture {self.numero_facture}"


class Remise(models.Model):
    """Discounts"""
    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=200)
    type_remise = models.CharField(max_length=20, choices=[
        ('pourcentage', 'Pourcentage'),
        ('montant_fixe', 'Montant fixe'),
    ])
    valeur = models.DecimalField(max_digits=10, decimal_places=2)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    utilisations_max = models.PositiveIntegerField(null=True, blank=True)
    utilisations_actuelles = models.PositiveIntegerField(default=0)
    formations_eligibles = models.ManyToManyField(Formation, blank=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Remise'
        verbose_name_plural = 'Remises'
    
    def __str__(self):
        return f"{self.code} - {self.description}"
    
    @property
    def utilisable(self):
        maintenant = timezone.now()
        return (self.active and 
                self.date_debut <= maintenant <= self.date_fin and
                (self.utilisations_max is None or 
                 self.utilisations_actuelles < self.utilisations_max))


class SponsoringOrganisation(models.Model):
    """Sponsorship relationships"""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    apprenant = models.ForeignKey(Apprenant, on_delete=models.CASCADE)
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE)
    pourcentage_prise_charge = models.DecimalField(max_digits=5, decimal_places=2)
    montant_prise_charge = models.DecimalField(max_digits=10, decimal_places=2)
    date_accord = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=50, choices=[
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
        ('paye', 'Payé'),
    ], default='en_attente')
    commentaire = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Sponsoring Organisation'
        verbose_name_plural = 'Sponsorings Organisations'
        unique_together = ['organisation', 'apprenant', 'formation']
    
    def __str__(self):
        return f"{self.organisation} sponsorise {self.apprenant} pour {self.formation}"
