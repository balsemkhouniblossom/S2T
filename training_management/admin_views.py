from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from users.models import Utilisateur, Formateur, Apprenant, Administrateur, Notification
from formations.models import Formation, Planning, Evaluation, Attestation, Salle
from courses.models import Cours, ProgressionCours
from messaging.models import Message, GroupeChat
from payments.models import Paiement, Facture


@login_required
def comprehensive_admin_dashboard(request):
    """Comprehensive admin dashboard showing everything"""
    try:
        admin = Administrateur.objects.get(utilisateur=request.user)
    except Administrateur.DoesNotExist:
        messages.error(request, 'Accès non autorisé. Vous devez être administrateur.')
        return redirect('users:dashboard')
    
    # Date ranges for analytics
    now = timezone.now()
    last_30_days = now - timedelta(days=30)
    last_7_days = now - timedelta(days=7)
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # ==================== USER METRICS ====================
    total_users = Utilisateur.objects.count()
    new_users_this_month = Utilisateur.objects.filter(date_joined__gte=this_month_start).count()
    active_users_30_days = Utilisateur.objects.filter(last_login__gte=last_30_days).count()
    
    formateurs_count = Formateur.objects.count()
    apprenants_count = Apprenant.objects.count()
    admins_count = Administrateur.objects.count()
    
    # Recent user registrations
    recent_users = Utilisateur.objects.order_by('-date_joined')[:10]
    
    # ==================== FORMATION METRICS ====================
    total_formations = Formation.objects.count()
    formations_publiees = Formation.objects.filter(statut='publiee').count()
    formations_en_cours = Formation.objects.filter(statut='en_cours').count()
    formations_terminees = Formation.objects.filter(statut='terminee').count()
    formations_brouillon = Formation.objects.filter(statut='brouillon').count()
    formations_annulees = Formation.objects.filter(statut='annulee').count()
    
    # Formation analytics
    formations_by_level = Formation.objects.values('niveau').annotate(count=Count('id'))
    popular_formations = Formation.objects.annotate(
        participant_count=Count('participants')
    ).order_by('-participant_count')[:5]
    
    # Recent formations
    recent_formations = Formation.objects.order_by('-date_creation')[:5]
    
    # ==================== COURSE METRICS ====================
    total_courses = Cours.objects.count()
    courses_publies = Cours.objects.filter(publie=True).count()
    
    # Course progression
    total_progressions = ProgressionCours.objects.count()
    completed_progressions = ProgressionCours.objects.filter(termine=True).count()
    course_completion_rate = (completed_progressions / max(total_progressions, 1)) * 100
    
    # ==================== FINANCIAL METRICS ====================
    total_revenue = Paiement.objects.filter(statut='complete').aggregate(
        total=Sum('montant')
    )['total'] or Decimal('0.00')
    
    monthly_revenue = Paiement.objects.filter(
        statut='complete',
        date_paiement__gte=this_month_start
    ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
    
    pending_payments = Paiement.objects.filter(statut='en_attente').count()
    failed_payments = Paiement.objects.filter(statut='echec').count()
    
    # Revenue by month (last 6 months)
    revenue_by_month = []
    for i in range(6):
        month_start = (now.replace(day=1) - timedelta(days=32*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_revenue = Paiement.objects.filter(
            statut='complete',
            date_paiement__gte=month_start,
            date_paiement__lte=month_end
        ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')
        revenue_by_month.append({
            'month': month_start.strftime('%m/%Y'),
            'revenue': float(month_revenue)
        })
    revenue_by_month.reverse()
    
    # ==================== MESSAGING METRICS ====================
    total_messages = Message.objects.count()
    messages_last_7_days = Message.objects.filter(date_envoi__gte=last_7_days).count()
    unread_messages = Message.objects.filter(lu=False).count()
    
    # ==================== EVALUATION METRICS ====================
    total_evaluations = Evaluation.objects.count()
    avg_rating = Evaluation.objects.aggregate(avg=Avg('note_globale'))['avg'] or 0
    
    # Top rated formations
    top_rated_formations = Formation.objects.annotate(
        avg_rating=Avg('evaluations__note_globale'),
        evaluation_count=Count('evaluations')
    ).filter(evaluation_count__gt=0).order_by('-avg_rating')[:5]
    
    # ==================== SYSTEM HEALTH ====================
    # Pending actions that need admin attention
    pending_actions = {
        'formations_brouillon': formations_brouillon,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
        'unread_messages': unread_messages,
    }
    
    # Recent activity
    recent_activity = []
    
    # Recent formations
    for formation in Formation.objects.order_by('-date_creation')[:3]:
        recent_activity.append({
            'type': 'formation',
            'message': f'Nouvelle formation créée: {formation.titre}',
            'date': formation.date_creation,
            'icon': 'graduation-cap',
            'color': 'success'
        })
    
    # Recent users
    for user in Utilisateur.objects.order_by('-date_joined')[:3]:
        recent_activity.append({
            'type': 'user',
            'message': f'Nouvel utilisateur inscrit: {user.get_full_name()}',
            'date': user.date_joined,
            'icon': 'user-plus',
            'color': 'info'
        })
    
    # Recent payments
    for payment in Paiement.objects.filter(statut='complete').order_by('-date_paiement')[:3]:
        recent_activity.append({
            'type': 'payment',
            'message': f'Paiement reçu: {payment.montant}€',
            'date': payment.date_paiement,
            'icon': 'credit-card',
            'color': 'warning'
        })
    
    # Sort recent activity by date
    recent_activity.sort(key=lambda x: x['date'], reverse=True)
    recent_activity = recent_activity[:10]
    
    # ==================== GROWTH METRICS ====================
    # User growth over last 12 months
    user_growth = []
    for i in range(12):
        month_start = (now.replace(day=1) - timedelta(days=32*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        month_users = Utilisateur.objects.filter(
            date_joined__gte=month_start,
            date_joined__lte=month_end
        ).count()
        user_growth.append({
            'month': month_start.strftime('%m/%Y'),
            'users': month_users
        })
    user_growth.reverse()
    
    # Formation enrollment trends
    enrollment_trends = []
    for i in range(6):
        month_start = (now.replace(day=1) - timedelta(days=32*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        enrollments = Formation.objects.filter(
            date_creation__gte=month_start,
            date_creation__lte=month_end
        ).aggregate(total_participants=Sum('participants__id'))['total_participants'] or 0
        enrollment_trends.append({
            'month': month_start.strftime('%m/%Y'),
            'enrollments': enrollments
        })
    enrollment_trends.reverse()
    
    # ==================== TRAINER PERFORMANCE ====================
    trainer_performance = Formateur.objects.annotate(
        formation_count=Count('formation'),
        avg_rating=Avg('formation__evaluations__note_formateur'),
        total_participants=Sum('formation__participants')
    ).order_by('-avg_rating')[:5]
    
    context = {
        # User metrics
        'total_users': total_users,
        'new_users_this_month': new_users_this_month,
        'active_users_30_days': active_users_30_days,
        'formateurs_count': formateurs_count,
        'apprenants_count': apprenants_count,
        'admins_count': admins_count,
        'recent_users': recent_users,
        
        # Formation metrics
        'total_formations': total_formations,
        'formations_publiees': formations_publiees,
        'formations_en_cours': formations_en_cours,
        'formations_terminees': formations_terminees,
        'formations_brouillon': formations_brouillon,
        'formations_annulees': formations_annulees,
        'formations_by_level': formations_by_level,
        'popular_formations': popular_formations,
        'recent_formations': recent_formations,
        
        # Course metrics
        'total_courses': total_courses,
        'courses_publies': courses_publies,
        'course_completion_rate': round(course_completion_rate, 1),
        
        # Financial metrics
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'pending_payments': pending_payments,
        'failed_payments': failed_payments,
        'revenue_by_month_json': json.dumps(revenue_by_month),
        
        # Messaging metrics
        'total_messages': total_messages,
        'messages_last_7_days': messages_last_7_days,
        'unread_messages': unread_messages,
        
        # Evaluation metrics
        'total_evaluations': total_evaluations,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'top_rated_formations': top_rated_formations,
        
        # System health
        'pending_actions': pending_actions,
        'recent_activity': recent_activity,
        
        # Analytics JSON data for charts
        'user_growth_json': json.dumps(user_growth),
        'enrollment_trends_json': json.dumps(enrollment_trends),
        'trainer_performance': trainer_performance,
    }
    
    return render(request, 'admin/comprehensive_dashboard.html', context)
