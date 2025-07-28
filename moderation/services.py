"""
AI Content Moderation Service
Provides intelligent content analysis and filtering capabilities
"""

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import (
    ContentModerationReport, 
    ContentModerationRule, 
    ContentModerationWhitelist,
    ModerationStats
)
import logging

logger = logging.getLogger(__name__)


class AIContentModerator:
    """Main AI content moderation service"""
    
    def __init__(self):
        self.rules = ContentModerationRule.objects.filter(active=True)
        self.whitelist = ContentModerationWhitelist.objects.filter(active=True)
    
    def moderate_content(self, content_object, content_text, author, content_type_label):
        """
        Moderate any content using AI analysis
        
        Args:
            content_object: The Django model instance containing the content
            content_text: The actual text content to analyze
            author: The Utilisateur who created the content
            content_type_label: Type label from ContentModerationReport.CONTENT_TYPE_CHOICES
        
        Returns:
            tuple: (is_safe, report) - is_safe is False if content should be blocked
        """
        if not content_text or not content_text.strip():
            return True, None
        
        # Check whitelist first
        if self._is_whitelisted(content_text, author):
            self._update_stats(checked=True)
            return True, None
        
        # Analyze content with all active rules
        all_issues = []
        max_confidence = 0.0
        max_severity = 'low'
        should_auto_block = False
        
        for rule in self.rules:
            violated, confidence, issues = rule.check_content(content_text)
            
            if violated:
                all_issues.extend(issues)
                max_confidence = max(max_confidence, confidence)
                
                # Determine severity level
                if rule.severity == 'critical':
                    max_severity = 'critical'
                elif rule.severity == 'high' and max_severity not in ['critical']:
                    max_severity = 'high'
                elif rule.severity == 'medium' and max_severity not in ['critical', 'high']:
                    max_severity = 'medium'
                
                if rule.auto_block:
                    should_auto_block = True
        
        # Create moderation report if issues found
        if all_issues:
            report = self._create_report(
                content_object=content_object,
                content_type_label=content_type_label,
                original_content=content_text,
                author=author,
                ai_confidence=max_confidence,
                detected_issues=all_issues,
                severity=max_severity,
                auto_blocked=should_auto_block
            )
            
            self._update_stats(checked=True, flagged=True, auto_blocked=should_auto_block)
            
            # Return False if content should be blocked
            return not should_auto_block, report
        
        # No issues found
        self._update_stats(checked=True)
        return True, None
    
    def moderate_course_comment(self, comment_instance):
        """Moderate course comments"""
        return self.moderate_content(
            content_object=comment_instance,
            content_text=comment_instance.commentaire,
            author=comment_instance.apprenant.utilisateur,
            content_type_label='course_comment'
        )
    
    def moderate_discussion_reply(self, reply_instance):
        """Moderate discussion replies"""
        return self.moderate_content(
            content_object=reply_instance,
            content_text=reply_instance.contenu,
            author=reply_instance.auteur,
            content_type_label='discussion_reply'
        )
    
    def moderate_group_message(self, message_instance):
        """Moderate group messages"""
        return self.moderate_content(
            content_object=message_instance,
            content_text=message_instance.contenu,
            author=message_instance.auteur,
            content_type_label='group_message'
        )
    
    def moderate_private_message(self, message_instance):
        """Moderate private messages"""
        return self.moderate_content(
            content_object=message_instance,
            content_text=message_instance.contenu,
            author=message_instance.expediteur,
            content_type_label='private_message'
        )
    
    def moderate_task_description(self, task_instance):
        """Moderate task descriptions"""
        return self.moderate_content(
            content_object=task_instance,
            content_text=f"{task_instance.titre} {task_instance.description}",
            author=task_instance.createur,
            content_type_label='task_description'
        )
    
    def _is_whitelisted(self, content, author):
        """Check if content or author is whitelisted"""
        # Check user whitelist
        user_whitelist = self.whitelist.filter(
            whitelist_type='user',
            value=author.email
        ).exists()
        
        if user_whitelist:
            return True
        
        # Check keyword/phrase whitelist
        content_lower = content.lower()
        
        for item in self.whitelist.filter(whitelist_type__in=['keyword', 'phrase']):
            if item.value.lower() in content_lower:
                return True
        
        return False
    
    def _create_report(self, content_object, content_type_label, original_content, 
                      author, ai_confidence, detected_issues, severity, auto_blocked):
        """Create a moderation report"""
        content_type = ContentType.objects.get_for_model(content_object)
        
        status = 'auto_filtered' if auto_blocked else 'pending'
        
        report = ContentModerationReport.objects.create(
            content_type=content_type,
            object_id=content_object.pk,
            content_type_label=content_type_label,
            original_content=original_content,
            author=author,
            ai_confidence=ai_confidence,
            detected_issues=detected_issues,
            severity=severity,
            status=status,
            auto_blocked=auto_blocked
        )
        
        logger.info(f"Content moderation report created: {report.id} - {severity} severity")
        return report
    
    def _update_stats(self, checked=False, flagged=False, auto_blocked=False):
        """Update daily moderation statistics"""
        today = timezone.now().date()
        
        stats, created = ModerationStats.objects.get_or_create(
            date=today,
            defaults={
                'total_content_checked': 0,
                'flagged_content': 0,
                'auto_blocked': 0,
                'human_reviewed': 0,
                'false_positives': 0,
            }
        )
        
        if checked:
            stats.total_content_checked += 1
        if flagged:
            stats.flagged_content += 1
        if auto_blocked:
            stats.auto_blocked += 1
        
        stats.save()
    
    def review_report(self, report_id, reviewer, decision, notes=""):
        """Human review of a moderation report"""
        try:
            report = ContentModerationReport.objects.get(id=report_id)
            
            report.reviewed_by = reviewer
            report.review_notes = notes
            report.review_date = timezone.now()
            
            if decision == 'approve':
                report.status = 'approved'
                # Unblock content if it was auto-blocked
                if report.auto_blocked:
                    self._unblock_content(report.content_object)
            elif decision == 'reject':
                report.status = 'rejected'
                # Block content if not already blocked
                if not report.auto_blocked:
                    self._block_content(report.content_object)
            
            report.save()
            
            # Update stats
            self._update_human_review_stats(report, decision)
            
            logger.info(f"Moderation report {report_id} reviewed: {decision}")
            return True
            
        except ContentModerationReport.DoesNotExist:
            logger.error(f"Moderation report {report_id} not found")
            return False
    
    def _block_content(self, content_object):
        """Block content (implementation depends on model)"""
        # This would be implemented based on each model's blocking mechanism
        # For example, setting an 'approved' field to False
        if hasattr(content_object, 'approuve'):
            content_object.approuve = False
            content_object.save()
        elif hasattr(content_object, 'active'):
            content_object.active = False
            content_object.save()
    
    def _unblock_content(self, content_object):
        """Unblock content (implementation depends on model)"""
        if hasattr(content_object, 'approuve'):
            content_object.approuve = True
            content_object.save()
        elif hasattr(content_object, 'active'):
            content_object.active = True
            content_object.save()
    
    def _update_human_review_stats(self, report, decision):
        """Update statistics for human reviews"""
        today = timezone.now().date()
        
        stats, created = ModerationStats.objects.get_or_create(
            date=today,
            defaults={
                'total_content_checked': 0,
                'flagged_content': 0,
                'auto_blocked': 0,
                'human_reviewed': 0,
                'false_positives': 0,
            }
        )
        
        stats.human_reviewed += 1
        
        if decision == 'approve' and report.severity in ['medium', 'high', 'critical']:
            stats.false_positives += 1
        
        stats.save()
    
    def get_moderation_dashboard_data(self):
        """Get data for moderation dashboard"""
        today = timezone.now().date()
        
        # Recent reports
        recent_reports = ContentModerationReport.objects.filter(
            created_at__date=today
        ).order_by('-created_at')[:10]
        
        # Pending reviews
        pending_reviews = ContentModerationReport.objects.filter(
            status='pending'
        ).count()
        
        # Today's stats
        today_stats = ModerationStats.objects.filter(date=today).first()
        if not today_stats:
            today_stats = ModerationStats(
                date=today,
                total_content_checked=0,
                flagged_content=0,
                auto_blocked=0,
                human_reviewed=0,
                false_positives=0
            )
        
        # Active rules
        active_rules = ContentModerationRule.objects.filter(active=True).count()
        
        return {
            'recent_reports': recent_reports,
            'pending_reviews': pending_reviews,
            'today_stats': today_stats,
            'active_rules': active_rules,
        }


# Global moderator instance
moderator = AIContentModerator()


def moderate_content_on_save(sender, instance, created, **kwargs):
    """Signal handler for automatic content moderation"""
    if not created:
        return  # Only moderate new content
    
    try:
        # Determine content type and moderate accordingly
        if sender.__name__ == 'CommentaireCours':
            is_safe, report = moderator.moderate_course_comment(instance)
            if not is_safe and report and report.auto_blocked:
                instance.approuve = False
                instance.save()
        
        elif sender.__name__ == 'ReponseDiscussion':
            is_safe, report = moderator.moderate_discussion_reply(instance)
            
        elif sender.__name__ == 'MessageGroupe':
            is_safe, report = moderator.moderate_group_message(instance)
            
        elif sender.__name__ == 'Message':
            is_safe, report = moderator.moderate_private_message(instance)
            
        elif sender.__name__ == 'Task':
            is_safe, report = moderator.moderate_task_description(instance)
    
    except Exception as e:
        logger.error(f"Error in content moderation: {e}")
