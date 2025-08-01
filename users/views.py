from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Utilisateur, Formateur, Apprenant, Administrateur, Notification, Reclamation
from formations.models import Formation
from courses.models import Cours, ProgressionCours, CommentaireCours
from messaging.models import Message, GroupeChat
from forum.models import ForumQuestion, ForumComment
from payments.models import Paiement
from .cv_extraction import extract_cv_info
from django.views.decorators.http import require_POST
from courses.quiz_models import Quiz, QuizResult, Certification, CertificationProgress, LearningGoal


@login_required
def user_details_view(request):
    users = Utilisateur.objects.all()
    user_data = []
    for user in users:
        # Basic info
        last_login = user.last_login
        date_joined = user.date_creation if hasattr(user, 'date_creation') else user.date_joined
        is_active = user.is_active
        status = user.confirmation if hasattr(user, 'confirmation') else ("Actif" if is_active else "Inactif")
        # Role/type
        role = ""
        try:
            if hasattr(user, 'apprenant'):
                role = "Apprenant"
            elif hasattr(user, 'formateur'):
                role = "Formateur"
            elif hasattr(user, 'administrateur'):
                role = "Administrateur"
        except Exception:
            role = "Utilisateur"
        # Courses enrolled and completed, total time spent
        courses = []
        completed_courses = 0
        total_time = 0
        organisation = None
        average_progress = 0
        mentor = None
        mentees = []
        try:
            apprenant = user.apprenant
            progressions = ProgressionCours.objects.filter(apprenant=apprenant)
            courses = [p.cours for p in progressions]
            completed_courses = progressions.filter(termine=True).count()
            total_time = sum(p.temps_passe_minutes for p in progressions)
            organisation = apprenant.organisation.nom if apprenant.organisation else None
            if progressions.exists():
                average_progress = sum(p.progression_pourcentage for p in progressions) / progressions.count()
            # Mentor (if any)
            from .models import Mentorship
            mentor_rel = Mentorship.objects.filter(mentee=user, active=True).first()
            mentor = mentor_rel.mentor if mentor_rel else None
        except Exception:
            pass
        # For trainers: mentees
        try:
            from .models import Mentorship
            mentee_rels = Mentorship.objects.filter(mentor=user, active=True)
            mentees = [rel.mentee for rel in mentee_rels]
        except Exception:
            pass
        # Messages sent (distinct recipients)
        messages_sent = Message.objects.filter(expediteur=user).values_list('destinataire', flat=True).distinct()
        recipients = Utilisateur.objects.filter(id__in=messages_sent)
        # Groups/roles
        groups = user.groupes_membre.all()
        # Forum interactions (questions + comments)
        forum_questions = ForumQuestion.objects.filter(auteur=user)
        forum_comments = ForumComment.objects.filter(auteur=user)
        forum_interactions = forum_questions.count() + forum_comments.count()
        # Most active forum topic
        most_active_topic = None
        if forum_comments.exists():
            topic_counts = {}
            for comment in forum_comments:
                title = comment.question.titre
                topic_counts[title] = topic_counts.get(title, 0) + 1
            if topic_counts:
                most_active_topic = max(topic_counts, key=topic_counts.get)
        # Course comments
        course_comments = CommentaireCours.objects.filter(apprenant__utilisateur=user).count()
        # Payments made
        payments = Paiement.objects.filter(apprenant__utilisateur=user).count()
        # Unread notifications
        unread_notifications = Notification.objects.filter(utilisateur=user, lu=False).count()
        # Complaints
        complaints = Reclamation.objects.filter(utilisateur=user).count()
        # Profile completion (simple: has photo, bio, phone, address)
        profile_fields = [user.photo_profil, user.telephone, user.adresse, user.date_naissance]
        profile_completion = int(sum(1 for f in profile_fields if f)) / len(profile_fields) * 100
        # Last password change
        last_password_change = user.last_password_change or user.last_login
        # Certificates (for apprenant or formateur)
        certificates = []
        try:
            if hasattr(user, 'apprenant'):
                certificates = [c.nom for c in user.apprenant.certification_set.all()]
            elif hasattr(user, 'formateur'):
                certificates = [c.nom for c in user.formateur.certifications.all()]
        except Exception:
            pass
        # Activity logs (last 5)
        activity_logs = list(user.activity_logs.order_by('-timestamp')[:5])
        # Badges
        badges = list(user.badges.all())
        # Admin notes/tags
        admin_note = user.admin_note
        custom_tags = user.custom_tags
        # Account lock/2FA/device info
        is_locked = user.is_locked
        failed_login_attempts = user.failed_login_attempts
        last_login_ip = user.last_login_ip
        last_login_device = user.last_login_device
        last_login_browser = user.last_login_browser
        two_factor_enabled = user.two_factor_enabled
        # Subscription/plan
        subscription_plan = user.subscription_plan
        subscription_renewal = user.subscription_renewal
        # GDPR/consent
        gdpr_consent = user.gdpr_consent
        marketing_consent = user.marketing_consent
        # Account deletion requests
        deletion_requested = user.account_deletion_requested
        # Add all to user_data
        user_data.append({
            'id': user.id,
            'prenom': user.prenom,
            'nom': user.nom,
            'email': user.email,
            'last_login': last_login,
            'date_joined': date_joined,
            'status': status,
            'role': role,
            'courses': courses,
            'completed_courses': completed_courses,
            'total_time': total_time,
            'organisation': organisation,
            'average_progress': average_progress,
            'mentor': mentor,
            'mentees': mentees,
            'messages_sent': recipients,
            'groups': groups,
            'forum_interactions': forum_interactions,
            'most_active_topic': most_active_topic,
            'course_comments': course_comments,
            'payments': payments,
            'unread_notifications': unread_notifications,
            'complaints': complaints,
            'profile_completion': profile_completion,
            'last_password_change': last_password_change,
            'certificates': certificates,
            'activity_logs': activity_logs,
            'badges': badges,
            'admin_note': admin_note,
            'custom_tags': custom_tags,
            'is_locked': is_locked,
            'failed_login_attempts': failed_login_attempts,
            'last_login_ip': last_login_ip,
            'last_login_device': last_login_device,
            'last_login_browser': last_login_browser,
            'two_factor_enabled': two_factor_enabled,
            'subscription_plan': subscription_plan,
            'subscription_renewal': subscription_renewal,
            'gdpr_consent': gdpr_consent,
            'marketing_consent': marketing_consent,
            'deletion_requested': deletion_requested,
        })
    return render(request, 'users/user_details.html', {'users': user_data})
from django.utils import timezone
from .forms import ReclamationForm


@login_required
def user_details_view(request):
    users = Utilisateur.objects.all()
    user_data = []
    for user in users:
        # Login count (assuming each login updates derniere_connexion, count by number of sessions or logins if tracked)
        login_count = user.last_login and 1 or 0  # Placeholder, replace with real login tracking if available

        # Courses enrolled (for Apprenant)
        courses = []
        try:
            apprenant = user.apprenant
            progressions = ProgressionCours.objects.filter(apprenant=apprenant)
            courses = [p.cours for p in progressions]
        except Exception:
            pass

        # Messages sent (distinct recipients)
        messages_sent = Message.objects.filter(expediteur=user).values_list('destinataire', flat=True).distinct()
        recipients = Utilisateur.objects.filter(id__in=messages_sent)

        # Groups
        groups = user.groupes_membre.all()

        # Forum interactions (questions + comments)
        forum_questions = ForumQuestion.objects.filter(auteur=user).count()
        forum_comments = ForumComment.objects.filter(auteur=user).count()
        forum_interactions = forum_questions + forum_comments

        # Course comments
        course_comments = CommentaireCours.objects.filter(apprenant__utilisateur=user).count()

        user_data.append({
            'id': user.id,
            'prenom': user.prenom,
            'nom': user.nom,
            'email': user.email,
            'login_count': login_count,
            'courses': courses,
            'messages_sent': recipients,
            'groups': groups,
            'forum_interactions': forum_interactions,
            'course_comments': course_comments,
        })
    return render(request, 'users/user_details.html', {'users': user_data})


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
                apprenant = Apprenant.objects.create(utilisateur=user)
                # Extract CV, experience, skills, and languages if available
                cv = request.FILES.get('cv')
                competences = request.POST.get('competences', '')
                experience = request.POST.get('experience', '')
                langues = request.POST.get('langues', '')
                motivation = request.POST.get('motivation', 'Je souhaite devenir formateur.')
                disponibilite = request.POST.get('disponibilite', '')
                # Create a generic TrainerApplication (not tied to a formation)
                from formations.models import TrainerApplication
                TrainerApplication.objects.create(
                    formation=None,  # Not tied to a specific formation
                    formateur=None,  # Not a formateur yet
                    message=f"Candidature automatique lors de l'inscription. CV: {cv}, Compétences: {competences}, Langues: {langues}",
                    motivation=motivation,
                    experience_pertinente=experience,
                    disponibilite=disponibilite,
                    statut='en_attente',
                    tarif_propose=None,
                    commentaire_admin='Classification automatique: Compétences: ' + competences + ', Expérience: ' + experience + ', Langues: ' + langues,
                )
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
            # Track login time
            user.derniere_connexion = timezone.now()
            user.save(update_fields=['derniere_connexion'])
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
    user = request.user
    if user.is_authenticated:
        user.derniere_deconnexion = timezone.now()
        user.save(update_fields=['derniere_deconnexion'])
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

        # Progressions for all courses
        progressions = ProgressionCours.objects.filter(apprenant=apprenant).select_related('cours')
        context['progressions'] = progressions

        # Quiz results
        quiz_results = QuizResult.objects.filter(apprenant=apprenant).select_related('quiz')
        context['quiz_results'] = quiz_results

        # Certifications
        certifications = Certification.objects.filter(cours__in=[p.cours for p in progressions])
        cert_progress = CertificationProgress.objects.filter(apprenant=apprenant, certification__in=certifications)
        context['certifications'] = certifications
        context['cert_progress'] = cert_progress

        # Learning goals (current week/month)
        from datetime import date
        today = date.today()
        goals = LearningGoal.objects.filter(apprenant=apprenant, date_debut__lte=today, date_fin__gte=today)
        context['learning_goals'] = goals

        # Analytics: total time, average daily engagement
        total_time = sum(p.temps_passe_minutes for p in progressions)
        context['total_time_minutes'] = total_time
        if progressions.exists():
            first_date = min([p.date_inscription for p in progressions])
            days_active = max((today - first_date.date()).days, 1)
            context['avg_daily_minutes'] = int(total_time / days_active)
        else:
            context['avg_daily_minutes'] = 0

        # Learning path: levels completed/in progress/locked
        niveaux = ['debutant', 'intermediaire', 'avance', 'expert']
        niveau_status = {}
        for niveau in niveaux:
            niveau_courses = Cours.objects.filter(niveau=niveau)
            completed = all(
                ProgressionCours.objects.filter(apprenant=apprenant, cours=c, termine=True).exists()
                for c in niveau_courses
            ) if niveau_courses.exists() else False
            in_progress = any(
                ProgressionCours.objects.filter(apprenant=apprenant, cours=c, termine=False).exists()
                for c in niveau_courses
            )
            if completed:
                niveau_status[niveau] = 'completed'
            elif in_progress:
                niveau_status[niveau] = 'in_progress'
            else:
                niveau_status[niveau] = 'locked'
        context['niveau_status'] = niveau_status

        # Calculate profile completion progression for apprenant
        user_fields = [user.nom, user.prenom, user.telephone, user.adresse, user.date_naissance, user.photo_profil]
        apprenant_fields = [apprenant.entreprise, apprenant.poste, apprenant.niveau_etude, apprenant.objectifs]
        total_fields = len(user_fields) + len(apprenant_fields)
        filled_fields = sum(1 for f in user_fields if f) + sum(1 for f in apprenant_fields if f)
        progression_profile = int((filled_fields / total_fields) * 100) if total_fields > 0 else 0
        context['progression_globale'] = progression_profile

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
        # Add user session history for attendance/participation
        from django.db.models import F
        context['user_sessions'] = Utilisateur.objects.all().annotate(user_id=F('pk')).values('user_id', 'nom', 'prenom', 'email', 'derniere_connexion', 'derniere_deconnexion', 'confirmation')
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

@login_required
def submit_reclamation(request):
    """Submit a new private reclamation to admin"""
    if request.method == 'POST':
        form = ReclamationForm(request.POST)
        if form.is_valid():
            reclamation = form.save(commit=False)
            reclamation.utilisateur = request.user
            reclamation.statut = 'ouverte'
            reclamation.save()
            messages.success(request, 'Réclamation soumise avec succès. Elle sera traitée par l\'administrateur.')
            return redirect('users:reclamation_list')
    else:
        form = ReclamationForm()
    return render(request, 'users/reclamation_form.html', {'form': form})

@login_required
def reclamation_list(request):
    """List user's own reclamations (apprenant/formateur) or all for admin"""
    user = request.user
    if hasattr(user, 'administrateur'):
        reclamations = Reclamation.objects.all()
    else:
        reclamations = Reclamation.objects.filter(utilisateur=user)
    return render(request, 'users/reclamation_list.html', {'reclamations': reclamations})

@login_required
def reclamation_detail(request, reclamation_id):
    """View details and admin response for a reclamation"""
    reclamation = get_object_or_404(Reclamation, pk=reclamation_id)
    is_admin = hasattr(request.user, 'administrateur')
    if request.method == 'POST' and is_admin:
        response = request.POST.get('response')
        if response:
            reclamation.statut = 'resolue'
            reclamation.description += f"\n\nRéponse de l'administrateur : {response}"
            reclamation.date_resolution = timezone.now()
            reclamation.save()
            messages.success(request, 'Réponse envoyée et réclamation résolue.')
            return redirect('users:reclamation_detail', reclamation_id=reclamation.id)
    return render(request, 'users/reclamation_detail.html', {'reclamation': reclamation, 'is_admin': is_admin})
