from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Utilisateur, Formateur, Apprenant, Administrateur, Notification
from formations.models import Formation
from courses.models import Cours
from messaging.models import Message
from payments.models import Paiement
from .cv_extraction import extract_cv_info
from django.views.decorators.http import require_POST


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        user_type = request.POST.get('user_type')
        
        if Utilisateur.objects.filter(email=email).exists():
            messages.error(request, 'Un utilisateur avec cet email existe déjà.')
        else:
            user = Utilisateur.objects.create_user(
                username=email,
                email=email,
                password=password,
                nom=nom,
                prenom=prenom
            )
            
            # Create specific user type
            if user_type == 'formateur':
                Formateur.objects.create(utilisateur=user)
            elif user_type == 'apprenant':
                Apprenant.objects.create(utilisateur=user)
            elif user_type == 'administrateur':
                Administrateur.objects.create(utilisateur=user)
            
            messages.success(request, 'Compte créé avec succès! Vous pouvez maintenant vous connecter.')
            return redirect('users:login')
    
    return render(request, 'auth/register.html')


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            
            # Redirect to role-specific dashboard
            try:
                formateur = Formateur.objects.get(utilisateur=user)
                messages.success(request, f'Bienvenue {user.prenom}! Accès formateur.')
                return redirect('users:dashboard')
            except Formateur.DoesNotExist:
                pass
            
            try:
                apprenant = Apprenant.objects.get(utilisateur=user)
                messages.success(request, f'Bienvenue {user.prenom}! Accès apprenant.')
                return redirect('users:dashboard')
            except Apprenant.DoesNotExist:
                pass
            
            try:
                admin = Administrateur.objects.get(utilisateur=user)
                messages.success(request, f'Bienvenue {user.prenom}! Accès administrateur.')
                return redirect('users:dashboard')
            except Administrateur.DoesNotExist:
                pass
            
            # Default redirect for users without specific roles
            messages.success(request, f'Bienvenue {user.prenom}!')
            return redirect('users:dashboard')
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')
    
    return render(request, 'auth/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('home')


@login_required
def dashboard_view(request):
    """Main dashboard view - redirects to role-specific dashboard"""
    user = request.user
    context = {'user': user}
    
    # Check user type and get relevant data
    try:
        formateur = Formateur.objects.get(utilisateur=user)
        context['user_type'] = 'formateur'
        context['formateur'] = formateur
        context['formations'] = Formation.objects.filter(formateur=formateur)[:5]  # Last 5
        context['courses'] = Cours.objects.filter(formateur=formateur)[:5]  # Last 5
        context['total_formations'] = Formation.objects.filter(formateur=formateur).count()
        context['total_courses'] = Cours.objects.filter(formateur=formateur).count()
        
        # Add trainer application context
        from formations.models import TrainerApplication, Task
        context['applications'] = TrainerApplication.objects.filter(formateur=formateur)
        context['available_opportunities'] = Formation.objects.filter(
            statut='proposition',
            applications_ouvertes=True
        ).exclude(
            trainer_applications__formateur=formateur
        )[:3]  # Show only 3 latest opportunities
        
        # Add tasks context
        context['tasks'] = Task.objects.filter(createur=user)
        
        return render(request, 'dashboard/formateur.html', context)
    except Formateur.DoesNotExist:
        pass
    
    try:
        apprenant = Apprenant.objects.get(utilisateur=user)
        context['user_type'] = 'apprenant'
        context['apprenant'] = apprenant
        context['formations'] = Formation.objects.filter(participants=apprenant)[:5]  # Last 5
        context['courses'] = Cours.objects.filter(progressions__apprenant=apprenant)[:5]  # Last 5
        context['total_formations'] = Formation.objects.filter(participants=apprenant).count()
        context['total_courses'] = Cours.objects.filter(progressions__apprenant=apprenant).count()
        
        # Add tasks context for apprenant
        from formations.models import Task
        context['tasks'] = Task.objects.filter(createur=user)
        
        return render(request, 'dashboard/apprenant.html', context)
    except Apprenant.DoesNotExist:
        pass
    
    try:
        admin = Administrateur.objects.get(utilisateur=user)
        context['user_type'] = 'administrateur'
        context['admin'] = admin
        context['stats'] = {
            'formations_count': Formation.objects.count(),
            'courses_count': Cours.objects.count(),
            'users_count': Utilisateur.objects.count(),
            'formateurs_count': Formateur.objects.count(),
            'apprenants_count': Apprenant.objects.count(),
            'recent_formations': Formation.objects.order_by('-date_creation')[:5],
            'recent_courses': Cours.objects.order_by('-date_creation')[:5],
        }
        return render(request, 'dashboard/administrateur.html', context)
    except Administrateur.DoesNotExist:
        pass
    
    # Default dashboard for users without specific roles
    context['user_type'] = 'default'
    context['message'] = 'Aucun rôle spécifique assigné. Contactez l\'administrateur.'
    return render(request, 'dashboard/default.html', context)


@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    context = {'user': user}
    
    # Get role-specific data
    try:
        formateur = Formateur.objects.get(utilisateur=user)
        context['user_type'] = 'formateur'
        context['formateur'] = formateur
    except Formateur.DoesNotExist:
        pass
    
    try:
        apprenant = Apprenant.objects.get(utilisateur=user)
        context['user_type'] = 'apprenant'
        context['apprenant'] = apprenant
    except Apprenant.DoesNotExist:
        pass
    
    try:
        admin = Administrateur.objects.get(utilisateur=user)
        context['user_type'] = 'administrateur'
        context['admin'] = admin
    except Administrateur.DoesNotExist:
        pass
    
    if request.method == 'POST':
        # Update basic user information
        user.nom = request.POST.get('nom', user.nom)
        user.prenom = request.POST.get('prenom', user.prenom)
        user.telephone = request.POST.get('telephone', user.telephone)
        user.adresse = request.POST.get('adresse', user.adresse)
        
        # Handle date of birth
        date_naissance = request.POST.get('date_naissance')
        if date_naissance:
            user.date_naissance = date_naissance
        
        # Handle profile photo
        if 'photo_profil' in request.FILES:
            user.photo_profil = request.FILES['photo_profil']
        
        user.save()
        
        # Update role-specific information
        if 'user_type' in context:
            if context['user_type'] == 'formateur' and 'formateur' in context:
                formateur = context['formateur']
                formateur.competences = request.POST.get('competences', formateur.competences)
                formateur.experience = request.POST.get('experience', formateur.experience)
                formateur.description = request.POST.get('description', formateur.description)
                formateur.tarif_horaire = request.POST.get('tarif_horaire', formateur.tarif_horaire)
                
                if 'cv' in request.FILES:
                    formateur.cv = request.FILES['cv']
                    formateur.save()
                    # Extract CV info after upload
                    try:
                        cv_path = formateur.cv.path
                        cv_data = extract_cv_info(cv_path)
                        # Show extracted info as a message (for demo)
                        messages.info(request, f"CV extrait: {cv_data}")
                    except Exception as e:
                        messages.warning(request, f"Erreur d'extraction du CV: {e}")
                else:
                    formateur.save()
            
            elif context['user_type'] == 'apprenant' and 'apprenant' in context:
                apprenant = context['apprenant']
                apprenant.entreprise = request.POST.get('entreprise', apprenant.entreprise)
                apprenant.poste = request.POST.get('poste', apprenant.poste)
                apprenant.niveau_etude = request.POST.get('niveau_etude', apprenant.niveau_etude)
                apprenant.objectifs = request.POST.get('objectifs', apprenant.objectifs)
                apprenant.save()
            
            elif context['user_type'] == 'administrateur' and 'admin' in context:
                admin = context['admin']
                admin.departement = request.POST.get('departement', admin.departement)
                admin.niveau_acces = request.POST.get('niveau_acces', admin.niveau_acces)
                admin.save()
        
        messages.success(request, 'Profil mis à jour avec succès!')
        return redirect('users:profile')
    
    return render(request, 'users/profile.html', context)


@login_required
def admin_user_list(request):
    # Only allow admins
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:profile')
    users = Utilisateur.objects.all().order_by('nom', 'prenom')
    return render(request, 'users/admin_user_list.html', {'users': users})

@require_POST
@login_required
def admin_user_activate(request, user_id):
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:admin_user_list')
    user = Utilisateur.objects.get(id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"Le compte de {user.get_full_name()} a été activé.")
    return redirect('users:admin_user_list')

@login_required
def admin_user_edit(request, user_id):
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:admin_user_list')
    user = Utilisateur.objects.get(id=user_id)
    formateur = Formateur.objects.filter(utilisateur=user).first()
    apprenant = Apprenant.objects.filter(utilisateur=user).first()
    admin_obj = Administrateur.objects.filter(utilisateur=user).first()

    # Determine role
    role = None
    if formateur:
        role = 'formateur'
    elif apprenant:
        role = 'apprenant'
    elif admin_obj:
        role = 'administrateur'

    if request.method == 'POST':
        # Always update common fields
        user.nom = request.POST.get('nom', user.nom)
        user.prenom = request.POST.get('prenom', user.prenom)
        user.email = request.POST.get('email', user.email)
        user.telephone = request.POST.get('telephone', user.telephone)
        user.adresse = request.POST.get('adresse', user.adresse)
        user.is_active = request.POST.get('is_active') == 'True'
        date_naissance = request.POST.get('date_naissance')
        if date_naissance:
            user.date_naissance = date_naissance
        if 'photo_profil' in request.FILES:
            user.photo_profil = request.FILES['photo_profil']
        user.save()

        # Only update fields for the user's role
        if role == 'formateur' and formateur:
            formateur.competences = request.POST.get('competences', formateur.competences)
            formateur.experience = request.POST.get('experience', formateur.experience)
            formateur.description = request.POST.get('description', formateur.description)
            formateur.tarif_horaire = request.POST.get('tarif_horaire', formateur.tarif_horaire)
            formateur.save()
        elif role == 'apprenant' and apprenant:
            apprenant.entreprise = request.POST.get('entreprise', apprenant.entreprise)
            apprenant.poste = request.POST.get('poste', apprenant.poste)
            apprenant.niveau_etude = request.POST.get('niveau_etude', apprenant.niveau_etude)
            apprenant.objectifs = request.POST.get('objectifs', apprenant.objectifs)
            apprenant.save()
        elif role == 'administrateur' and admin_obj:
            admin_obj.departement = request.POST.get('departement', admin_obj.departement)
            admin_obj.niveau_acces = request.POST.get('niveau_acces', admin_obj.niveau_acces)
            admin_obj.save()

        messages.success(request, 'Utilisateur mis à jour avec succès.')
        return redirect('users:admin_user_list')

    # Pass the role to the template for conditional rendering
    return render(request, 'users/admin_user_edit.html', {
        'user': user,
        'formateur': formateur,
        'apprenant': apprenant,
        'admin_obj': admin_obj,
        'role': role
    })
