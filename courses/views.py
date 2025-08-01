from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
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
            return redirect('courses:my_courses')
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
        return redirect('courses:my_courses')
    context = {'course': course}
    return render(request, 'courses/delete.html', context)

def courses_list(request):
    """List all published courses"""
    courses = Cours.objects.filter(publie=True).order_by('-date_creation')
    
    # Search functionality
    query = request.GET.get('search')
    if query:
        courses = courses.filter(
            Q(titre__icontains=query) | 
            Q(description__icontains=query) |
            Q(categorie__icontains=query) |
            Q(mots_cles__icontains=query)
        )
    
    # Filter by category
    categorie = request.GET.get('categorie')
    if categorie:
        courses = courses.filter(categorie=categorie)
    
    # Filter by level
    niveau = request.GET.get('niveau')
    if niveau:
        courses = courses.filter(niveau=niveau)
    
    # Get categories for filter
    categories = courses.values_list('categorie', flat=True).distinct()
    
    is_admin = hasattr(request.user, 'administrateur') or request.user.is_superuser
    is_formateur = hasattr(request.user, 'formateur')
    context = {
        'courses': courses,
        'categories': categories,
        'niveaux': Cours._meta.get_field('niveau').choices,
        'query': query,
        'selected_categorie': categorie,
        'selected_niveau': niveau,
        'is_admin': is_admin,
        'is_formateur': is_formateur,
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
    """Watch course content"""
    course = get_object_or_404(Cours, id=course_id, publie=True)
    
    try:
        apprenant = Apprenant.objects.get(utilisateur=request.user)
        progress = get_object_or_404(ProgressionCours, cours=course, apprenant=apprenant)
    except Apprenant.DoesNotExist:
        messages.error(request, 'Accès refusé.')
        return redirect('courses:detail', course_id=course_id)
    
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
