
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Formation, Salle, Planning, Presence, Evaluation, Attestation, TrainerApplication, Task
from payments.models import Organisation
from .forms import AdminFormationForm, TrainerApplicationForm, TrainerApplicationReviewForm, TaskForm, TaskFilterForm, FormationForm
from users.models import Formateur, Apprenant, Administrateur

# Stub admin evaluations list view
@staff_member_required
def admin_evaluations_list(request):
    return render(request, 'formations/admin/evaluations_list.html')

# Stub admin attendance list view
@staff_member_required
def admin_attendance_list(request):
    return render(request, 'formations/admin/attendance_list.html')


def formations_list(request):
    """List all available formations"""
    formations = Formation.objects.filter(statut='publiee').order_by('-date_creation')
    
    # Search functionality
    query = request.GET.get('search')
    if query:
        formations = formations.filter(
            Q(titre__icontains=query) | 
            Q(description__icontains=query) |
            Q(formateur__utilisateur__nom__icontains=query)
        )
    
    # Filter by level
    niveau = request.GET.get('niveau')
    if niveau:
        formations = formations.filter(niveau=niveau)
    
    context = {
        'formations': formations,
        'niveaux': Formation._meta.get_field('niveau').choices,
        'query': query,
        'selected_niveau': niveau,
    }
    return render(request, 'formations/list.html', context)


def formation_detail(request, formation_id):
    """Formation detail view"""
    formation = get_object_or_404(Formation, id=formation_id)
    user_enrolled = False
    user_can_enroll = False
    
    if request.user.is_authenticated:
        try:
            apprenant = Apprenant.objects.get(utilisateur=request.user)
            user_enrolled = formation.participants.filter(id=apprenant.id).exists()
            user_can_enroll = not user_enrolled and formation.places_restantes > 0
        except Apprenant.DoesNotExist:
            pass
    
    context = {
        'formation': formation,
        'user_enrolled': user_enrolled,
        'user_can_enroll': user_can_enroll,
        'sessions': formation.sessions.all().order_by('date_session'),
    }
    return render(request, 'formations/detail.html', context)


@login_required
def formation_enroll(request, formation_id):
    """Enroll in a formation"""
    formation = get_object_or_404(Formation, id=formation_id)
    
    try:
        apprenant = Apprenant.objects.get(utilisateur=request.user)
        
        if formation.participants.filter(id=apprenant.id).exists():
            messages.warning(request, 'Vous êtes déjà inscrit à cette formation.')
        elif formation.places_restantes <= 0:
            messages.error(request, 'Cette formation est complète.')
        else:
            formation.participants.add(apprenant)
            messages.success(request, f'Inscription réussie à la formation "{formation.titre}"!')
    except Apprenant.DoesNotExist:
        messages.error(request, 'Seuls les apprenants peuvent s\'inscrire aux formations.')
    
    return redirect('formations:detail', formation_id=formation_id)


@login_required
def my_formations(request):
    """User's enrolled formations"""
    formations = []
    user_type = None
    
    try:
        formateur = Formateur.objects.get(utilisateur=request.user)
        formations = Formation.objects.filter(formateur=formateur)
        user_type = 'formateur'
    except Formateur.DoesNotExist:
        try:
            apprenant = Apprenant.objects.get(utilisateur=request.user)
            formations = Formation.objects.filter(participants=apprenant)
            user_type = 'apprenant'
        except Apprenant.DoesNotExist:
            pass
    
    context = {
        'formations': formations,
        'user_type': user_type,
    }
    return render(request, 'formations/my_formations.html', context)



from .forms import FormationForm

@login_required
def formation_create(request):
    """Create a new formation (formateurs only)"""
    try:
        formateur = Formateur.objects.get(utilisateur=request.user)
    except Formateur.DoesNotExist:
        messages.error(request, 'Seuls les formateurs peuvent créer des formations.')
        return redirect('formations_list')

    if request.method == 'POST':
        form = FormationForm(request.POST)
        if form.is_valid():
            formation = form.save(commit=False)
            formation.formateur = formateur
            formation.save()
            messages.success(request, 'Formation créée avec succès!')
            return redirect('formations:detail', formation_id=formation.id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = FormationForm()

    context = {
        'form': form,
        'niveaux': Formation._meta.get_field('niveau').choices,
    }
    return render(request, 'formations/create.html', context)


# ============================================
# ADMIN VIEWS FOR FORMATION MANAGEMENT
# ============================================

@login_required
def admin_formations_dashboard(request):
    """Admin dashboard for formation management"""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:dashboard')
    
    # Get statistics
    formations = Formation.objects.all()
    stats = {
        'total_formations': formations.count(),
        'formations_brouillon': formations.filter(statut='brouillon').count(),
        'formations_publiees': formations.filter(statut='publiee').count(),
        'formations_en_cours': formations.filter(statut='en_cours').count(),
        'formations_terminees': formations.filter(statut='terminee').count(),
        'total_formateurs': Formateur.objects.count(),
        'total_participants': sum(f.participants_inscrits for f in formations),
    }
    
    # Recent formations
    recent_formations = formations.order_by('-date_creation')[:5]
    
    context = {
        'stats': stats,
        'recent_formations': recent_formations,
    }
    return render(request, 'formations/admin/dashboard.html', context)


@login_required
def admin_formations_list(request):
    """Admin view to list all formations"""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:dashboard')
    
    formations = Formation.objects.select_related('formateur__utilisateur').order_by('-date_creation')
    
    # Search and filter
    query = request.GET.get('search')
    if query:
        formations = formations.filter(
            Q(titre__icontains=query) | 
            Q(description__icontains=query) |
            Q(formateur__utilisateur__nom__icontains=query) |
            Q(formateur__utilisateur__prenom__icontains=query)
        )
    
    statut = request.GET.get('statut')
    if statut:
        formations = formations.filter(statut=statut)
        
    niveau = request.GET.get('niveau')
    if niveau:
        formations = formations.filter(niveau=niveau)
    
    # Pagination
    paginator = Paginator(formations, 10)
    page_number = request.GET.get('page')
    formations_page = paginator.get_page(page_number)
    
    context = {
        'formations': formations_page,
        'statuts': Formation._meta.get_field('statut').choices,
        'niveaux': Formation._meta.get_field('niveau').choices,
        'query': query,
        'selected_statut': statut,
        'selected_niveau': niveau,
    }
    return render(request, 'formations/admin/list.html', context)


@login_required
def admin_formation_create(request):
    """Admin view to create a new formation"""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = AdminFormationForm(request.POST)
        if form.is_valid():
            formation = form.save()
            messages.success(request, f'Formation "{formation.titre}" créée avec succès!')
            return redirect('formations:admin_formation_detail', formation_id=formation.id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = AdminFormationForm()
    
    context = {
        'form': form,
        'title': 'Créer une nouvelle formation',
        'action_url': 'formations:admin_formation_create',
    }
    return render(request, 'formations/admin/form.html', context)


@login_required
def admin_formation_detail(request, formation_id):
    """Admin view for formation details"""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:dashboard')
    
    formation = get_object_or_404(Formation, id=formation_id)
    
    # Get sessions/planning
    sessions = Planning.objects.filter(formation=formation).order_by('date_session')
    
    # Get evaluations summary
    evaluations = Evaluation.objects.filter(formation=formation)
    avg_ratings = {
        'contenu': evaluations.aggregate(avg=Avg('note_contenu'))['avg'],
        'formateur': evaluations.aggregate(avg=Avg('note_formateur'))['avg'],
        'organisation': evaluations.aggregate(avg=Avg('note_organisation'))['avg'],
        'globale': evaluations.aggregate(avg=Avg('note_globale'))['avg'],
    }
    
    context = {
        'formation': formation,
        'sessions': sessions,
        'evaluations_count': evaluations.count(),
        'avg_ratings': avg_ratings,
        'participants_count': formation.participants_inscrits,
        'places_restantes': formation.places_restantes,
    }
    return render(request, 'formations/admin/detail.html', context)


@login_required
def admin_formation_edit(request, formation_id):
    """Admin view to edit a formation"""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:dashboard')
    
    formation = get_object_or_404(Formation, id=formation_id)
    
    if request.method == 'POST':
        form = AdminFormationForm(request.POST, instance=formation)
        if form.is_valid():
            formation = form.save()
            messages.success(request, f'Formation "{formation.titre}" modifiée avec succès!')
            return redirect('formations:admin_formation_detail', formation_id=formation.id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = AdminFormationForm(instance=formation)
    
    context = {
        'form': form,
        'formation': formation,
        'title': f'Modifier la formation: {formation.titre}',
        'action_url': 'formations:admin_formation_edit',
    }
    return render(request, 'formations/admin/form.html', context)


@login_required
def admin_formation_delete(request, formation_id):
    """Admin view to delete a formation"""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:dashboard')
    
    formation = get_object_or_404(Formation, id=formation_id)
    
    if request.method == 'POST':
        titre = formation.titre
        formation.delete()
        messages.success(request, f'Formation "{titre}" supprimée avec succès!')
        return redirect('formations:admin_list')
    
    context = {
        'formation': formation,
        'participants_count': formation.participants_inscrits,
    }
    return render(request, 'formations/admin/delete_confirm.html', context)


@login_required
def admin_assign_trainer(request):
    """Admin view to assign trainers to formations"""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        formation_id = request.POST.get('formation_id')
        formateur_id = request.POST.get('formateur_id')
        
        try:
            formation = Formation.objects.get(id=formation_id)
            formateur = Formateur.objects.get(id=formateur_id)
            
            formation.formateur = formateur
            formation.save()
            
            messages.success(request, f'Formateur {formateur.utilisateur.get_full_name()} assigné à la formation "{formation.titre}"')
            return JsonResponse({'success': True})
        except (Formation.DoesNotExist, Formateur.DoesNotExist) as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # GET request - show assignment interface
    formations = Formation.objects.filter(statut__in=['brouillon', 'publiee'])
    formateurs = Formateur.objects.select_related('utilisateur').all()
    
    context = {
        'formations': formations,
        'formateurs': formateurs,
    }
    return render(request, 'formations/admin/assign_trainer.html', context)


# ============================================
# TRAINER APPLICATION VIEWS
# ============================================

@login_required
def available_formations(request):
    """View available formations for trainer applications"""
    try:
        formateur = Formateur.objects.get(utilisateur=request.user)
    except Formateur.DoesNotExist:
        messages.error(request, 'Seuls les formateurs peuvent voir les opportunités.')
        return redirect('formations:list')
    
    # Get formations open for applications
    formations = Formation.objects.filter(
        statut='proposition',
        applications_ouvertes=True,
        formateur__isnull=True
    ).exclude(
        trainer_applications__formateur=formateur
    )
    
    # Filter by deadline
    formations = formations.filter(
        Q(date_limite_candidature__isnull=True) | 
        Q(date_limite_candidature__gt=timezone.now())
    )
    
    # Search functionality
    query = request.GET.get('search')
    if query:
        formations = formations.filter(
            Q(titre__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Filter by level
    niveau = request.GET.get('niveau')
    if niveau:
        formations = formations.filter(niveau=niveau)
    
    # Get user's applications
    user_applications = TrainerApplication.objects.filter(
        formateur=formateur
    ).select_related('formation')
    
    context = {
        'formations': formations,
        'user_applications': user_applications,
        'niveaux': Formation._meta.get_field('niveau').choices,
        'query': query,
        'selected_niveau': niveau,
    }
    return render(request, 'formations/available_formations.html', context)


@login_required
def apply_for_formation(request, formation_id):
    """Apply for a formation"""
    try:
        formateur = Formateur.objects.get(utilisateur=request.user)
    except Formateur.DoesNotExist:
        messages.error(request, 'Seuls les formateurs peuvent candidater.')
        return redirect('formations:list')
    
    formation = get_object_or_404(Formation, id=formation_id)
    
    # Check if formation is open for applications
    if not formation.is_open_for_applications:
        messages.error(request, 'Cette formation n\'accepte plus de candidatures.')
        return redirect('formations:available_formations')
    
    # Check if user already applied
    if TrainerApplication.objects.filter(formation=formation, formateur=formateur).exists():
        messages.warning(request, 'Vous avez déjà candidaté pour cette formation.')
        return redirect('formations:available_formations')
    
    if request.method == 'POST':
        form = TrainerApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.formation = formation
            application.formateur = formateur
            application.save()
            
            messages.success(request, f'Votre candidature pour "{formation.titre}" a été envoyée avec succès!')
            return redirect('formations:my_applications')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = TrainerApplicationForm()
    
    context = {
        'form': form,
        'formation': formation,
    }
    return render(request, 'formations/apply_formation.html', context)


@login_required
def my_applications(request):
    """View trainer's applications"""
    try:
        formateur = Formateur.objects.get(utilisateur=request.user)
    except Formateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé.')
        return redirect('formations:list')
    
    applications = TrainerApplication.objects.filter(
        formateur=formateur
    ).select_related('formation').order_by('-date_candidature')
    
    # Filter by status
    statut = request.GET.get('statut')
    if statut:
        applications = applications.filter(statut=statut)
    
    context = {
        'applications': applications,
        'statuts': TrainerApplication._meta.get_field('statut').choices,
        'selected_statut': statut,
    }
    return render(request, 'formations/my_applications.html', context)


@login_required
def application_detail(request, application_id):
    """View application details"""
    try:
        formateur = Formateur.objects.get(utilisateur=request.user)
        application = TrainerApplication.objects.select_related('formation').get(
            id=application_id, 
            formateur=formateur
        )
    except (Formateur.DoesNotExist, TrainerApplication.DoesNotExist):
        messages.error(request, 'Candidature introuvable.')
        return redirect('formations:my_applications')
    
    context = {
        'application': application,
    }
    return render(request, 'formations/application_detail.html', context)


@login_required
def withdraw_application(request, application_id):
    """Withdraw a trainer application"""
    try:
        formateur = Formateur.objects.get(utilisateur=request.user)
        application = TrainerApplication.objects.get(
            id=application_id, 
            formateur=formateur,
            statut='en_attente'
        )
        
        application.statut = 'retiree'
        application.save()
        
        messages.success(request, 'Votre candidature a été retirée.')
    except (Formateur.DoesNotExist, TrainerApplication.DoesNotExist):
        messages.error(request, 'Impossible de retirer cette candidature.')
    
    return redirect('formations:my_applications')


# ============================================
# ADMIN VIEWS FOR TRAINER APPLICATIONS
# ============================================

@login_required
def admin_applications_list(request):
    """Admin view to manage trainer applications"""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:dashboard')
    
    applications = TrainerApplication.objects.select_related(
        'formation', 'formateur__utilisateur'
    ).order_by('-date_candidature')
    
    # Filter by status
    statut = request.GET.get('statut')
    if statut:
        applications = applications.filter(statut=statut)
    
    # Filter by formation
    formation_id = request.GET.get('formation')
    if formation_id:
        applications = applications.filter(formation_id=formation_id)
    
    # Get formations with applications
    formations_with_apps = Formation.objects.filter(
        trainer_applications__isnull=False
    ).distinct()
    
    context = {
        'applications': applications,
        'formations': formations_with_apps,
        'statuts': TrainerApplication._meta.get_field('statut').choices,
        'selected_statut': statut,
        'selected_formation': formation_id,
    }
    return render(request, 'formations/admin/applications_list.html', context)


@login_required
def admin_application_review(request, application_id):
    """Admin view to review a trainer application"""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:dashboard')
    
    application = get_object_or_404(
        TrainerApplication.objects.select_related('formation', 'formateur__utilisateur'),
        id=application_id
    )
    
    if request.method == 'POST':
        form = TrainerApplicationReviewForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save(commit=False)
            application.date_reponse = timezone.now()
            application.save()
            
            # If accepted, assign trainer to formation
            if application.statut == 'acceptee':
                formation = application.formation
                formation.formateur = application.formateur
                formation.statut = 'publiee'  # Change status to published
                formation.save()
                
                # Reject other applications for this formation
                TrainerApplication.objects.filter(
                    formation=formation,
                    statut='en_attente'
                ).exclude(id=application.id).update(
                    statut='rejetee',
                    commentaire_admin='Formation assignée à un autre formateur',
                    date_reponse=timezone.now()
                )
            
            messages.success(request, 'Candidature traitée avec succès!')
            return redirect('formations:admin_applications_list')
        else:
            messages.error(request, 'Veuillez corriger les erreurs dans le formulaire.')
    else:
        form = TrainerApplicationReviewForm(instance=application)
    
    context = {
        'application': application,
        'form': form,
    }
    return render(request, 'formations/admin/application_review.html', context)


@login_required
def withdraw_application(request, application_id):
    """Allow trainer to withdraw their application"""
    try:
        formateur = Formateur.objects.get(utilisateur=request.user)
    except Formateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être formateur.')
        return redirect('users:dashboard')
    
    application = get_object_or_404(TrainerApplication, id=application_id, formateur=formateur)
    
    if application.statut != 'en_attente':
        messages.error(request, 'Seules les candidatures en attente peuvent être retirées.')
        return redirect('formations:application_detail', application_id=application_id)
    
    # Withdraw the application
    application.statut = 'retiree'
    application.date_reponse = timezone.now()
    application.save()
    
    messages.success(request, 'Votre candidature a été retirée avec succès.')
    return redirect('formations:my_applications')


# Task Management Views

@login_required
def task_list(request):
    """List all tasks for the current user"""
    user = request.user
    
    # Get tasks created by the user
    tasks = Task.objects.filter(createur=user)
    
    # Apply filters
    filter_form = TaskFilterForm(request.GET)
    if filter_form.is_valid():
        if filter_form.cleaned_data['statut']:
            tasks = tasks.filter(statut=filter_form.cleaned_data['statut'])
        if filter_form.cleaned_data['priorite']:
            tasks = tasks.filter(priorite=filter_form.cleaned_data['priorite'])
        if filter_form.cleaned_data['categorie']:
            tasks = tasks.filter(categorie=filter_form.cleaned_data['categorie'])
        if filter_form.cleaned_data['date_debut']:
            tasks = tasks.filter(date_creation__gte=filter_form.cleaned_data['date_debut'])
        if filter_form.cleaned_data['date_fin']:
            tasks = tasks.filter(date_creation__lte=filter_form.cleaned_data['date_fin'])
        if filter_form.cleaned_data['recherche']:
            search_term = filter_form.cleaned_data['recherche']
            tasks = tasks.filter(
                Q(titre__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(notes__icontains=search_term)
            )
    
    # Order tasks
    order_by = request.GET.get('order_by', '-date_creation')
    tasks = tasks.order_by(order_by)
    
    # Pagination
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total': tasks.count(),
        'todo': tasks.filter(statut='todo').count(),
        'in_progress': tasks.filter(statut='in_progress').count(),
        'completed': tasks.filter(statut='completed').count(),
        'overdue': len([task for task in tasks if task.is_overdue]),
    }
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'stats': stats,
        'user_type': get_user_type(user),
    }
    
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    """Create a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.createur = request.user
            task.save()
            messages.success(request, 'Tâche créée avec succès!')
            return redirect('formations:task_detail', task_id=task.id)
    else:
        form = TaskForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Créer une nouvelle tâche',
        'user_type': get_user_type(request.user),
    }
    
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_detail(request, task_id):
    """View task details"""
    task = get_object_or_404(Task, id=task_id, createur=request.user)
    
    context = {
        'task': task,
        'user_type': get_user_type(request.user),
    }
    
    return render(request, 'tasks/task_detail.html', context)


@login_required
def task_edit(request, task_id):
    """Edit an existing task"""
    task = get_object_or_404(Task, id=task_id, createur=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tâche modifiée avec succès!')
            return redirect('formations:task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task, user=request.user)
    
    context = {
        'form': form,
        'task': task,
        'title': 'Modifier la tâche',
        'user_type': get_user_type(request.user),
    }
    
    return render(request, 'tasks/task_form.html', context)


@login_required
def task_delete(request, task_id):
    """Delete a task"""
    task = get_object_or_404(Task, id=task_id, createur=request.user)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Tâche supprimée avec succès!')
        return redirect('formations:task_list')
    
    context = {
        'task': task,
        'user_type': get_user_type(request.user),
    }
    
    return render(request, 'tasks/task_delete_confirm.html', context)


@login_required
def task_toggle_status(request, task_id):
    """Toggle task status via AJAX"""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, createur=request.user)
        
        import json
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status in [choice[0] for choice in Task.STATUS_CHOICES]:
            task.statut = new_status
            if new_status == 'completed':
                task.date_completion = timezone.now()
            elif task.statut == 'completed' and new_status != 'completed':
                task.date_completion = None
            task.save()
            
            return JsonResponse({
                'success': True,
                'new_status': task.get_statut_display(),
                'status_class': task.get_status_badge_class()
            })
    
    return JsonResponse({'success': False})


@login_required
def task_dashboard(request):
    """Task dashboard with overview and quick actions"""
    user = request.user
    tasks = Task.objects.filter(createur=user)
    
    # Recent tasks
    recent_tasks = tasks.order_by('-date_creation')[:5]
    
    # Upcoming deadlines
    upcoming_tasks = tasks.filter(
        date_echeance__isnull=False,
        statut__in=['todo', 'in_progress']
    ).order_by('date_echeance')[:5]
    
    # Overdue tasks
    overdue_tasks = [task for task in tasks if task.is_overdue]
    
    # Statistics
    stats = {
        'total_tasks': tasks.count(),
        'todo_tasks': tasks.filter(statut='todo').count(),
        'in_progress_tasks': tasks.filter(statut='in_progress').count(),
        'completed_tasks': tasks.filter(statut='completed').count(),
        'overdue_tasks': len(overdue_tasks),
        'completion_rate': (
            tasks.filter(statut='completed').count() / tasks.count() * 100
            if tasks.count() > 0 else 0
        ),
    }
    
    # Tasks by category
    tasks_by_category = tasks.values('categorie').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Tasks by priority
    tasks_by_priority = tasks.values('priorite').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Kanban tasks for drag-and-drop
    kanban_tasks = {
        'todo': tasks.filter(statut='todo'),
        'in_progress': tasks.filter(statut='in_progress'),
        'completed': tasks.filter(statut='completed'),
    }

    context = {
        'recent_tasks': recent_tasks,
        'upcoming_tasks': upcoming_tasks,
        'overdue_tasks': overdue_tasks[:5],  # Limit to 5 for display
        'stats': stats,
        'tasks_by_category': tasks_by_category,
        'tasks_by_priority': tasks_by_priority,
        'user_type': get_user_type(user),
        'kanban_tasks': kanban_tasks,
    }

    return render(request, 'tasks/task_dashboard.html', context)


def get_user_type(user):
    """Helper function to get user type"""
    try:
        if hasattr(user, 'formateur'):
            return 'formateur'
        elif hasattr(user, 'apprenant'):
            return 'apprenant'
        elif hasattr(user, 'administrateur'):
            return 'administrateur'
    except:
        pass
    return 'user'


def formation_unenroll(request, formation_id):
    """Unenroll the current user from a formation."""
    formation = get_object_or_404(Formation, id=formation_id)
    user = request.user
    if not user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour vous désinscrire.")
        return redirect('users:login')
    apprenant = getattr(user, 'apprenant', None)
    if apprenant and formation.participants.filter(id=apprenant.id).exists():
        formation.participants.remove(apprenant)
        messages.success(request, "Vous vous êtes désinscrit de la formation.")
    else:
        messages.warning(request, "Vous n'êtes pas inscrit à cette formation.")
    return redirect('formations:detail', formation_id=formation.id)


def organisation_enroll(request, formation_id):
    """Enroll an apprenant in a formation via organization code (pending until confirmed)."""
    formation = get_object_or_404(Formation, id=formation_id)
    if not request.user.is_authenticated:
        messages.error(request, "Vous devez être connecté pour vous inscrire via une organisation.")
        return redirect('users:login')
    apprenant = getattr(request.user, 'apprenant', None)
    if not apprenant:
        messages.error(request, "Seuls les apprenants peuvent s'inscrire via une organisation.")
        return redirect('formations:detail', formation_id=formation.id)
    # TODO: OrganisationEnrollmentForm and OrganisationEnrollment model are missing. Implement or import the correct form/model.
    raise NotImplementedError("OrganisationEnrollmentForm is not defined. Please implement or import the correct form/model.")


def organisation_enroll_confirm(request, enrollment_id):
    """Show confirmation and status for an organisation enrollment."""
    # TODO: OrganisationEnrollment model is missing. Implement or import the correct model.
    raise NotImplementedError("OrganisationEnrollment model is not defined. Please implement or import the correct model.")


@require_POST
@login_required
def admin_formation_status_update(request, formation_id):
    """Admin action to update the status of a formation."""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('formations:admin_list')

    formation = get_object_or_404(Formation, id=formation_id)
    new_status = request.POST.get('statut')
    valid_statuses = [choice[0] for choice in Formation._meta.get_field('statut').choices]
    if new_status in valid_statuses:
        formation.statut = new_status
        formation.save()
        messages.success(request, f"Le statut de la formation '{formation.titre}' a été mis à jour.")
    else:
        messages.error(request, "Statut invalide.")
    return redirect('formations:admin_list')


@require_POST
@login_required
def admin_formation_bulk_status_update(request):
    """Admin action to bulk update the status of selected formations."""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('formations:admin_list')

    formation_ids = request.POST.getlist('formation_ids')
    new_status = request.POST.get('bulk_statut')
    valid_statuses = [choice[0] for choice in Formation._meta.get_field('statut').choices]
    if not formation_ids or not new_status or new_status not in valid_statuses:
        messages.error(request, "Veuillez sélectionner au moins une formation et un statut valide.")
        return redirect('formations:admin_list')

    updated = Formation.objects.filter(id__in=formation_ids).update(statut=new_status)
    messages.success(request, f"Statut mis à jour pour {updated} formation(s).")
    return redirect('formations:admin_list')


@login_required
def admin_sessions_list(request):
    """Stub admin sessions list page."""
    return render(request, 'formations/admin/sessions_list.html')
