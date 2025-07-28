from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Message, GroupeChat, MessageGroupe, FilDiscussion, ReponseDiscussion
from users.models import Utilisateur


@login_required
def messages_inbox(request):
    """User's message inbox"""
    # Get all conversations (unique users the current user has exchanged messages with)
    conversations = Message.objects.filter(
        Q(expediteur=request.user) | Q(destinataire=request.user)
    ).values('expediteur', 'destinataire').distinct()
    
    # Create a list of conversation partners
    conversation_list = []
    for conv in conversations:
        if conv['expediteur'] == request.user.id:
            partner_id = conv['destinataire']
        else:
            partner_id = conv['expediteur']
        
        # Get the partner user
        try:
            partner = Utilisateur.objects.get(id=partner_id)
            # Get the latest message in this conversation
            latest_message = Message.objects.filter(
                Q(expediteur=request.user, destinataire=partner) |
                Q(expediteur=partner, destinataire=request.user)
            ).order_by('-date_envoi').first()
            
            # Count unread messages
            unread_count = Message.objects.filter(
                expediteur=partner,
                destinataire=request.user,
                lu=False
            ).count()
            
            conversation_list.append({
                'partner': partner,
                'latest_message': latest_message,
                'unread_count': unread_count
            })
        except Utilisateur.DoesNotExist:
            continue
    
    # Sort by latest message date
    conversation_list.sort(key=lambda x: x['latest_message'].date_envoi if x['latest_message'] else timezone.now(), reverse=True)
    
    context = {
        'conversations': conversation_list,
    }
    return render(request, 'messaging/inbox.html', context)


@login_required
def chat_conversation(request, user_id):
    """Chat conversation view between two users"""
    other_user = get_object_or_404(Utilisateur, id=user_id)
    
    # Get all messages between the two users
    messages_list = Message.objects.filter(
        Q(expediteur=request.user, destinataire=other_user) |
        Q(expediteur=other_user, destinataire=request.user)
    ).order_by('date_envoi')
    
    # Mark messages as read
    unread_messages = Message.objects.filter(
        expediteur=other_user,
        destinataire=request.user,
        lu=False
    )
    unread_messages.update(lu=True, date_lecture=timezone.now())
    
    # Handle new message
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            message = Message.objects.create(
                expediteur=request.user,
                destinataire=other_user,
                sujet=f"Message de {request.user.get_full_name()}",
                contenu=contenu,
            )
            
            if 'fichier_joint' in request.FILES:
                message.fichier_joint = request.FILES['fichier_joint']
                message.save()
            
            # Redirect to refresh the page and show the new message
            return redirect('messaging:chat_conversation', user_id=user_id)
    
    context = {
        'other_user': other_user,
        'messages': messages_list,
        'conversation_title': f"Chat avec {other_user.get_full_name()}",
    }
    return render(request, 'messaging/chat_interface.html', context)


@login_required
def message_detail(request, message_id):
    """Message detail view"""
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user has permission to view this message
    if message.destinataire != request.user and message.expediteur != request.user:
        messages.error(request, 'Vous n\'avez pas accès à ce message.')
        return redirect('messaging:inbox')
    
    # Mark as read if user is the recipient
    if message.destinataire == request.user and not message.lu:
        message.lu = True
        message.save()
    
    return render(request, 'messaging/message_detail.html', {'message': message})


@login_required
def message_compose(request):
    """Compose new message"""
    if request.method == 'POST':
        destinataire_id = request.POST.get('destinataire')
        sujet = request.POST.get('sujet')
        contenu = request.POST.get('contenu')
        # Handle missing destinataire_id
        if not destinataire_id:
            messages.error(request, 'Veuillez sélectionner un destinataire.')
            users = Utilisateur.objects.exclude(id=request.user.id).values('id', 'email', 'nom', 'prenom')
            return render(request, 'messaging/compose.html', {
                'users': users,
                'sujet': sujet,
                'contenu': contenu,
            })
        try:
            destinataire = Utilisateur.objects.get(id=destinataire_id)
            message = Message.objects.create(
                expediteur=request.user,
                destinataire=destinataire,
                sujet=sujet,
                contenu=contenu,
            )
            if 'fichier_joint' in request.FILES:
                message.fichier_joint = request.FILES['fichier_joint']
                message.save()
            messages.success(request, 'Message envoyé avec succès!')
            return redirect('messaging:inbox')
        except Utilisateur.DoesNotExist:
            messages.error(request, 'Utilisateur introuvable.')
            users = Utilisateur.objects.exclude(id=request.user.id).values('id', 'email', 'nom', 'prenom')
            return render(request, 'messaging/compose.html', {
                'users': users,
                'sujet': sujet,
                'contenu': contenu,
            })
    # Get list of users for autocomplete
    users = Utilisateur.objects.exclude(id=request.user.id).values('id', 'email', 'nom', 'prenom')
    return render(request, 'messaging/compose.html', {'users': users})


@login_required
def groups_list(request):
    """List user's group chats"""
    groups = GroupeChat.objects.filter(
        Q(membres=request.user) | Q(createur=request.user)
    ).distinct().order_by('-date_creation')
    
    context = {
        'groups': groups,
    }
    return render(request, 'messaging/groups.html', context)


@login_required
def group_detail(request, group_id):
    """Group chat detail view"""
    group = get_object_or_404(GroupeChat, id=group_id)
    
    # Check if user is a member
    if not (group.membres.filter(id=request.user.id).exists() or group.createur == request.user):
        messages.error(request, 'Vous n\'êtes pas membre de ce groupe.')
        return redirect('messaging:groups')
    
    # Get group messages
    group_messages = group.messages.all().order_by('date_envoi')
    
    # Handle new message
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            message = MessageGroupe.objects.create(
                groupe=group,
                auteur=request.user,
                contenu=contenu,
            )
            
            if 'fichier_joint' in request.FILES:
                message.fichier_joint = request.FILES['fichier_joint']
                message.save()
            
            messages.success(request, 'Message envoyé!')
            return redirect('messaging:group_detail', group_id=group_id)
    
    context = {
        'group': group,
        'group_messages': group_messages,
    }
    return render(request, 'messaging/group_detail.html', context)


@login_required
def discussions_list(request):
    """List discussion threads"""
    discussions = FilDiscussion.objects.all().order_by('-epingle', '-derniere_reponse')
    
    # Search functionality
    query = request.GET.get('search')
    if query:
        discussions = discussions.filter(
            Q(titre__icontains=query) | Q(contenu__icontains=query)
        )
    
    context = {
        'discussions': discussions,
        'query': query,
    }
    return render(request, 'messaging/discussions.html', context)


@login_required
def discussion_detail(request, discussion_id):
    """Discussion thread detail view"""
    discussion = get_object_or_404(FilDiscussion, id=discussion_id)
    
    # Increment view count
    discussion.nb_vues += 1
    discussion.save()
    
    # Get replies
    reponses = discussion.reponses.all().order_by('date_creation')
    
    # Handle new reply
    if request.method == 'POST':
        contenu = request.POST.get('contenu')
        if contenu:
            reponse = ReponseDiscussion.objects.create(
                discussion=discussion,
                auteur=request.user,
                contenu=contenu,
            )
            
            if 'fichier_joint' in request.FILES:
                reponse.fichier_joint = request.FILES['fichier_joint']
                reponse.save()
            
            # Update last reply time
            discussion.derniere_reponse = reponse.date_creation
            discussion.save()
            
            messages.success(request, 'Réponse ajoutée!')
            return redirect('messaging:discussion_detail', discussion_id=discussion_id)
    
    context = {
        'discussion': discussion,
        'reponses': reponses,
    }
    return render(request, 'messaging/discussion_detail.html', context)
