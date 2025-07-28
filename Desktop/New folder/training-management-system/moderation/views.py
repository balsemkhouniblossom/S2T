
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import ContentModerationReport, ContentModerationRule, ModerationStats
from .services import moderator
import json

@staff_member_required
def admin_complaints_list(request):
    # Stub admin complaints list view
    return render(request, 'moderation/admin_complaints_list.html')


@staff_member_required
def moderation_dashboard(request):
    """Main moderation dashboard"""
    dashboard_data = moderator.get_moderation_dashboard_data()
    
    # Get weekly stats
    week_ago = timezone.now().date() - timezone.timedelta(days=7)
    weekly_stats = ModerationStats.objects.filter(
        date__gte=week_ago
    ).order_by('-date')
    
    context = {
        'recent_reports': dashboard_data['recent_reports'],
        'pending_reviews': dashboard_data['pending_reviews'],
        'today_stats': dashboard_data['today_stats'],
        'active_rules': dashboard_data['active_rules'],
        'weekly_stats': weekly_stats,
    }
    
    return render(request, 'moderation/dashboard.html', context)


@staff_member_required
def pending_reports(request):
    """View pending moderation reports"""
    reports = ContentModerationReport.objects.filter(
        status='pending'
    ).order_by('-created_at')
    
    # Filter by severity if requested
    severity_filter = request.GET.get('severity')
    if severity_filter:
        reports = reports.filter(severity=severity_filter)
    
    # Filter by content type if requested
    content_type_filter = request.GET.get('content_type')
    if content_type_filter:
        reports = reports.filter(content_type_label=content_type_filter)
    
    # Pagination
    paginator = Paginator(reports, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'severity_filter': severity_filter,
        'content_type_filter': content_type_filter,
        'severity_choices': ContentModerationReport.SEVERITY_CHOICES,
        'content_type_choices': ContentModerationReport.CONTENT_TYPE_CHOICES,
    }
    
    return render(request, 'moderation/pending_reports.html', context)


@staff_member_required
def review_report(request, report_id):
    """Review a specific moderation report"""
    report = get_object_or_404(ContentModerationReport, id=report_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action in ['approve', 'reject']:
            success = moderator.review_report(report_id, request.user, action, notes)
            
            if success:
                messages.success(request, f'Rapport {action} avec succès')
                return redirect('moderation:pending_reports')
            else:
                messages.error(request, 'Erreur lors de la révision')
    
    context = {
        'report': report,
    }
    
    return render(request, 'moderation/review_report.html', context)


@staff_member_required
def moderation_stats(request):
    """View moderation statistics"""
    # Get last 30 days of stats
    thirty_days_ago = timezone.now().date() - timezone.timedelta(days=30)
    stats = ModerationStats.objects.filter(
        date__gte=thirty_days_ago
    ).order_by('-date')
    
    # Calculate totals
    total_checked = sum(stat.total_content_checked for stat in stats)
    total_flagged = sum(stat.flagged_content for stat in stats)
    total_auto_blocked = sum(stat.auto_blocked for stat in stats)
    total_human_reviewed = sum(stat.human_reviewed for stat in stats)
    total_false_positives = sum(stat.false_positives for stat in stats)
    
    # Calculate rates
    flagging_rate = (total_flagged / total_checked * 100) if total_checked > 0 else 0
    auto_block_rate = (total_auto_blocked / total_flagged * 100) if total_flagged > 0 else 0
    false_positive_rate = (total_false_positives / total_human_reviewed * 100) if total_human_reviewed > 0 else 0
    
    context = {
        'stats': stats,
        'total_checked': total_checked,
        'total_flagged': total_flagged,
        'total_auto_blocked': total_auto_blocked,
        'total_human_reviewed': total_human_reviewed,
        'total_false_positives': total_false_positives,
        'flagging_rate': flagging_rate,
        'auto_block_rate': auto_block_rate,
        'false_positive_rate': false_positive_rate,
    }
    
    return render(request, 'moderation/stats.html', context)


@staff_member_required
def test_content(request):
    """Test content moderation on sample text"""
    if request.method == 'POST':
        test_text = request.POST.get('test_text', '')
        
        if test_text:
            # Use a dummy object for testing
            class DummyContent:
                pk = 0
                def save(self):
                    pass
            
            dummy_obj = DummyContent()
            
            # Test moderation
            is_safe, report = moderator.moderate_content(
                content_object=dummy_obj,
                content_text=test_text,
                author=request.user,
                content_type_label='test'
            )
            
            # If report was created, delete it (it's just a test)
            if report:
                report.delete()
            
            # Prepare response data
            response_data = {
                'is_safe': is_safe,
                'detected_issues': []
            }
            
            if report:
                response_data.update({
                    'ai_confidence': report.ai_confidence,
                    'severity': report.get_severity_display(),
                    'detected_issues': report.detected_issues,
                    'would_auto_block': report.auto_blocked
                })
            
            return JsonResponse(response_data)
    
    # Get all active rules for display
    active_rules = ContentModerationRule.objects.filter(active=True)
    
    context = {
        'active_rules': active_rules,
    }
    
    return render(request, 'moderation/test_content.html', context)


def api_moderate_content(request):
    """API endpoint for content moderation (for AJAX calls)"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        content_text = data.get('content', '')
        content_type = data.get('content_type', 'test')
        
        if not content_text:
            return JsonResponse({'error': 'No content provided'}, status=400)
        
        # Use dummy object for API testing
        class DummyContent:
            pk = 0
            def save(self):
                pass
        
        dummy_obj = DummyContent()
        
        # Moderate content
        is_safe, report = moderator.moderate_content(
            content_object=dummy_obj,
            content_text=content_text,
            author=request.user if request.user.is_authenticated else None,
            content_type_label=content_type
        )
        
        response_data = {
            'is_safe': is_safe,
            'blocked': False
        }
        
        if report:
            response_data.update({
                'confidence': report.ai_confidence,
                'severity': report.severity,
                'issues': report.detected_issues,
                'blocked': report.auto_blocked
            })
            # Clean up test report
            report.delete()
        
        return JsonResponse(response_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def test_content(request):
    """Test content moderation interface"""
    active_rules = ContentModerationRule.objects.filter(is_active=True)
    return render(request, 'moderation/test_content.html', {
        'active_rules': active_rules
    })
