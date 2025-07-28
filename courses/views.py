from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from .models import Cours, RessourceCours, ProgressionCours, CommentaireCours
from users.models import Formateur, Apprenant


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
    
    context = {
        'courses': courses,
        'categories': categories,
        'niveaux': Cours._meta.get_field('niveau').choices,
        'query': query,
        'selected_categorie': categorie,
        'selected_niveau': niveau,
    }
    return render(request, 'courses/list.html', context)


def course_detail(request, course_id):
    """Course detail view"""
    course = get_object_or_404(Cours, id=course_id, publie=True)
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
    
    context = {
        'course': course,
        'user_enrolled': user_enrolled,
        'user_progress': user_progress,
        'ressources': ressources,
        'commentaires': commentaires,
        'avg_rating': round(avg_rating, 1),
        'total_comments': commentaires.count(),
    }
    return render(request, 'courses/detail.html', context)


@login_required
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
    
    return redirect('course_detail', course_id=course_id)


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
def course_create(request):
    """Create a new course (formateurs only)"""
    try:
        formateur = Formateur.objects.get(utilisateur=request.user)
    except Formateur.DoesNotExist:
        messages.error(request, 'Seuls les formateurs peuvent créer des cours.')
        return redirect('courses_list')
    
    if request.method == 'POST':
        course = Cours.objects.create(
            titre=request.POST.get('titre'),
            description=request.POST.get('description'),
            contenu=request.POST.get('contenu'),
            formateur=formateur,
            duree_minutes=request.POST.get('duree_minutes'),
            niveau=request.POST.get('niveau'),
            categorie=request.POST.get('categorie'),
            mots_cles=request.POST.get('mots_cles', ''),
            prix=request.POST.get('prix', 0),
            gratuit=request.POST.get('gratuit') == 'on',
        )
        
        if 'image_couverture' in request.FILES:
            course.image_couverture = request.FILES['image_couverture']
            course.save()
        
        messages.success(request, 'Cours créé avec succès!')
        return redirect('course_detail', course_id=course.id)
    
    context = {
        'niveaux': Cours._meta.get_field('niveau').choices,
    }
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
        return redirect('course_detail', course_id=course_id)
    
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
