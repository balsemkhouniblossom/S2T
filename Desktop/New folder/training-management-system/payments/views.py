from django.views.decorators.http import require_POST
from django.contrib import messages

@require_POST
def activate_enrollment(request, inscription_id):
    from formations.models import Inscription
    inscription = Inscription.objects.get(pk=inscription_id)
    inscription.activate()
    messages.success(request, f"Inscription activée pour {inscription.apprenant} dans {inscription.formation}.")
    return redirect('payments:dashboard')
from django.shortcuts import render, redirect
from .forms import SponsoringOrganisationForm, PaiementForm

def create_sponsorship(request):
    if request.method == 'POST':
        form = SponsoringOrganisationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payments:dashboard')
    else:
        form = SponsoringOrganisationForm()
    return render(request, 'payments/sponsorship_form.html', {'form': form})

def create_paiement(request):
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payments:dashboard')
    else:
        form = PaiementForm()
    return render(request, 'payments/paiement_form.html', {'form': form})
from .models import Paiement, Organisation

def payments_dashboard(request):
    """Custom dashboard for payments management."""
    total_payments = Paiement.objects.count()
    total_amount = Paiement.objects.filter(statut='valide').aggregate(models.Sum('montant'))['montant__sum'] or 0
    org_count = Organisation.objects.count()
    recent_payments = Paiement.objects.order_by('-date_paiement')[:10]
    # Pending enrollments: Inscription with statut 'en_attente' and a valid Paiement
    from formations.models import Inscription, Formation
    pending_enrollments = []
    for inscription in Inscription.objects.filter(statut='en_attente'):
        paiement = Paiement.objects.filter(
            formation=inscription.formation,
            apprenant=inscription.apprenant,
            statut__in=['valide', 'en_attente']
        ).order_by('-date_paiement').first()
        if paiement:
            inscription.paiement = paiement
            pending_enrollments.append(inscription)
    context = {
        'total_payments': total_payments,
        'total_amount': total_amount,
        'org_count': org_count,
        'recent_payments': recent_payments,
        'pending_enrollments': pending_enrollments,
    }
    return render(request, 'payments/dashboard.html', context)

from django.shortcuts import render
from django.db import models

def admin_list(request):
    # Stub admin payments list view
    return render(request, 'payments/admin_list.html')
