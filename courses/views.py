from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Sum
from .models import Cours, RessourceCours, ProgressionCours, CommentaireCours
from users.models import Formateur, Apprenant, Administrateur

from django.contrib.auth.decorators import user_passes_test

def is_admin_or_formateur(user):
    return user.is_superuser or hasattr(user, 'formateur') or hasattr(user, 'administrateur')
from .forms import CoursForm

@login_required
@user_passes_test(is_admin_or_formateur)
def course_edit(request, course_id):
    """Edit a course (admins/formateurs only)"""
    course = get_object_or_404(Cours, id=course_id)
    # Only allow superuser, admin, or the course's formateur to edit
    if not (request.user.is_superuser or hasattr(request.user, 'administrateur') or (hasattr(request.user, 'formateur') and course.formateur == request.user.formateur)):
        messages.error(request, 'Vous ne pouvez modifier que vos propres cours.')
        return redirect('courses:my_courses')
    if request.method == 'POST':
        form = CoursForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cours modifié avec succès!')
            return redirect('courses:list')
    else:
        form = CoursForm(instance=course)
    context = {'form': form, 'course': course}
    return render(request, 'courses/edit.html', context)

@login_required
@user_passes_test(is_admin_or_formateur)
def course_delete(request, course_id):
    """Delete a course (admins/formateurs only)"""
    course = get_object_or_404(Cours, id=course_id)
    # Only allow superuser, admin, or the course's formateur to delete
    if not (request.user.is_superuser or hasattr(request.user, 'administrateur') or (hasattr(request.user, 'formateur') and course.formateur == request.user.formateur)):
        messages.error(request, 'Vous ne pouvez supprimer que vos propres cours.')
        return redirect('courses:my_courses')
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Cours supprimé avec succès!')
    return redirect('courses:list')
    context = {'course': course}
    return render(request, 'courses/delete.html', context)

def courses_list(request):
    """List courses (all for admins, own+published for formateurs, published for others)"""
    user = request.user
    is_admin = hasattr(user, 'administrateur') or user.is_superuser
    is_formateur = hasattr(user, 'formateur')

    if user.is_authenticated and is_admin:
        courses = Cours.objects.all().order_by('-date_creation')
    elif user.is_authenticated and is_formateur:
        # Show published courses plus the formateur's own (even if not published)
        courses = Cours.objects.filter(
            Q(publie=True) | Q(formateur=user.formateur)
        ).order_by('-date_creation')
    else:
        courses = Cours.objects.filter(publie=True).order_by('-date_creation')

    # Search functionality (support both 'q' from template and legacy 'search')
    query = request.GET.get('q') or request.GET.get('search')
    if query:
        courses = courses.filter(
            Q(titre__icontains=query)
            | Q(description__icontains=query)
            | Q(categorie__icontains=query)
            | Q(mots_cles__icontains=query)
        )

    # Filter by level (matches template's name="niveau")
    niveau = request.GET.get('niveau')
    if niveau:
        courses = courses.filter(niveau=niveau)

    # Filter by duration range (name="duree_min"/"duree_max" in template)
    duree_min = request.GET.get('duree_min')
    if duree_min:
        try:
            courses = courses.filter(duree_minutes__gte=int(duree_min))
        except ValueError:
            pass
    duree_max = request.GET.get('duree_max')
    if duree_max:
        try:
            courses = courses.filter(duree_minutes__lte=int(duree_max))
        except ValueError:
            pass

    # Filter by formateur (name="formateur" in template)
    formateur_id = request.GET.get('formateur')
    if formateur_id:
        try:
            courses = courses.filter(formateur_id=int(formateur_id))
        except ValueError:
            pass

    # Data for filters
    categories = courses.values_list('categorie', flat=True).distinct()
    formateurs = Formateur.objects.all().select_related('utilisateur')
    # Aggregated stats (site-wide for published courses)
    total_courses = Cours.objects.filter(publie=True).count()
    total_formateurs = (
        Cours.objects.filter(publie=True)
        .values_list('formateur_id', flat=True)
        .distinct()
        .count()
    )
    total_minutes = Cours.objects.filter(publie=True).aggregate(total=Sum('duree_minutes'))['total'] or 0
    total_hours = round(total_minutes / 60.0, 1)
    site_avg_rating = (
        CommentaireCours.objects.filter(approuve=True, cours__publie=True)
        .aggregate(avg=Avg('note'))['avg'] or 0
    )

    # Enrolled course IDs for the current apprenant (used by template to show Continuer/Commencer)
    enrolled_course_ids = []
    if user.is_authenticated:
        try:
            apprenant = Apprenant.objects.get(utilisateur=user)
            enrolled_course_ids = list(
                ProgressionCours.objects.filter(apprenant=apprenant).values_list('cours_id', flat=True)
            )
        except Apprenant.DoesNotExist:
            pass

    context = {
        'courses': courses,
        'categories': categories,
        'niveaux': Cours._meta.get_field('niveau').choices,
        'query': query,
        'selected_niveau': niveau,
        'is_admin': is_admin,
        'is_formateur': is_formateur,
        'formateurs': formateurs,
        'enrolled_course_ids': enrolled_course_ids,
    'total_courses': total_courses,
    'total_formateurs': total_formateurs,
    'total_hours': total_hours,
    'site_avg_rating': round(site_avg_rating, 1) if site_avg_rating else 0,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, course_id):
    """Course detail view"""
    course = get_object_or_404(Cours, id=course_id)
    user_enrolled = False
    user_progress = None
    
    if request.user.is_authenticated:
        try:
            apprenant = Apprenant.objects.get(utilisateur=request.user)
            user_progress = ProgressionCours.objects.filter(
                cours=course, 
                apprenant=apprenant
            ).first()
            user_enrolled = user_progress is not None
        except Apprenant.DoesNotExist:
            pass
    
    # Get course resources
    ressources = course.ressources.all().order_by('ordre')
    
    # Get course comments
    commentaires = course.commentaires.filter(approuve=True).order_by('-date_creation')
    
    # Calculate average rating
    avg_rating = commentaires.aggregate(Avg('note'))['note__avg'] or 0
    
    is_admin = request.user.is_superuser or hasattr(request.user, 'administrateur')
    is_formateur = hasattr(request.user, 'formateur')
    can_manage = is_admin or (is_formateur and course.formateur == getattr(request.user, 'formateur', None))
    context = {
        'course': course,
        'user_enrolled': user_enrolled,
        'user_progress': user_progress,
        'ressources': ressources,
        'commentaires': commentaires,
        'avg_rating': round(avg_rating, 1),
        'total_comments': commentaires.count(),
        'is_admin': is_admin,
        'is_formateur': is_formateur,
        'can_manage': can_manage,
    }
    return render(request, 'courses/detail.html', context)


@login_required
@user_passes_test(lambda u: hasattr(u, 'apprenant'))
def course_enroll(request, course_id):
    """Enroll in a course"""
    course = get_object_or_404(Cours, id=course_id, publie=True)
    
    try:
        apprenant = Apprenant.objects.get(utilisateur=request.user)
        
        # Check if already enrolled
        if ProgressionCours.objects.filter(cours=course, apprenant=apprenant).exists():
            messages.warning(request, 'Vous êtes déjà inscrit à ce cours.')
        else:
            ProgressionCours.objects.create(cours=course, apprenant=apprenant)
            messages.success(request, f'Inscription réussie au cours "{course.titre}"!')
    except Apprenant.DoesNotExist:
        messages.error(request, 'Seuls les apprenants peuvent s\'inscrire aux cours.')
    
    return redirect('courses:detail', course_id=course_id)


@login_required
def my_courses(request):
    """User's enrolled courses"""
    courses = []
    user_type = None
    
    try:
        formateur = Formateur.objects.get(utilisateur=request.user)
        courses = Cours.objects.filter(formateur=formateur)
        user_type = 'formateur'
    except Formateur.DoesNotExist:
        try:
            apprenant = Apprenant.objects.get(utilisateur=request.user)
            progressions = ProgressionCours.objects.filter(apprenant=apprenant).select_related('cours')
            courses = [p.cours for p in progressions]
            user_type = 'apprenant'
        except Apprenant.DoesNotExist:
            pass
    
    context = {
        'courses': courses,
        'user_type': user_type,
    }
    return render(request, 'courses/my_courses.html', context)


@login_required
@user_passes_test(is_admin_or_formateur)
def course_create(request):
    """Create a new course (admins/formateurs only)"""
    formateur = None
    if hasattr(request.user, 'formateur'):
        formateur = request.user.formateur
    elif hasattr(request.user, 'administrateur'):
        # Optionally, admins can select a formateur or assign themselves
        pass
    else:
        messages.error(request, 'Seuls les formateurs ou administrateurs peuvent créer des cours.')
        return redirect('courses:my_courses')

    if request.method == 'POST':
        form = CoursForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            if formateur:
                course.formateur = formateur
            course.save()
            messages.success(request, 'Cours créé avec succès!')
            return redirect('courses:detail', course_id=course.id)
    else:
        form = CoursForm()

    context = {'form': form}
    return render(request, 'courses/create.html', context)


@login_required
def course_watch(request, course_id):
    """Watch course content. Allow if course is published OR the user is already enrolled."""
    course = Cours.objects.filter(id=course_id).first()
    if not course:
        messages.error(request, "Ce cours n'existe pas ou a été supprimé.")
        return redirect('courses:list')

    try:
        apprenant = Apprenant.objects.get(utilisateur=request.user)
    except Apprenant.DoesNotExist:
        messages.error(request, 'Accès refusé.')
        return redirect('courses:detail', course_id=course_id)

    # If the course is not published, only allow access if the learner is already enrolled
    if not course.publie:
        if not ProgressionCours.objects.filter(cours=course, apprenant=apprenant).exists():
            messages.error(request, "Ce cours n'est pas encore publié.")
            return redirect('courses:detail', course_id=course_id)

    progress = get_object_or_404(ProgressionCours, cours=course, apprenant=apprenant)

    # Get course resources
    ressources = course.ressources.all().order_by('ordre')

    # Update last activity
    progress.save()  # This will update derniere_activite

    context = {
        'course': course,
        'progress': progress,
        'ressources': ressources,
    }
    return render(request, 'courses/watch.html', context)
