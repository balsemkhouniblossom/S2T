from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ForumQuestion, ForumComment
from users.models import Utilisateur

@login_required
def forum_list(request):
    questions = ForumQuestion.objects.order_by('-date_creation')
    return render(request, 'forum/forum_list.html', {'questions': questions})

@login_required
def forum_detail(request, question_id):
    question = get_object_or_404(ForumQuestion, pk=question_id)
    comments = question.commentaires.order_by('date_creation')
    return render(request, 'forum/forum_detail.html', {'question': question, 'comments': comments})

@login_required
def forum_post_question(request):
    if request.method == 'POST':
        titre = request.POST.get('titre')
        contenu = request.POST.get('contenu')
        ForumQuestion.objects.create(auteur=request.user, titre=titre, contenu=contenu)
        return redirect('forum:list')
    return render(request, 'forum/forum_post_question.html')

@login_required
def forum_post_comment(request, question_id):
    question = get_object_or_404(ForumQuestion, pk=question_id)
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        ForumComment.objects.create(auteur=request.user, question=question, contenu=contenu)
        return redirect('forum:detail', question_id=question_id)
    return render(request, 'forum/forum_post_comment.html', {'question': question})
