from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    ContentModerationReport,
    ContentModerationRule,
    ContentModerationWhitelist,
    ModerationStats
)
from .services import moderator


@admin.register(ContentModerationReport)
class ContentModerationReportAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'content_type_label', 'author', 'severity_badge', 
        'status_badge', 'ai_confidence_display', 'auto_blocked',
        'created_at', 'review_actions'
    ]
    list_filter = [
        'content_type_label', 'severity', 'status', 'auto_blocked',
        'created_at', 'review_date'
    ]
    search_fields = [
        'original_content', 'author__nom', 'author__prenom', 
        'author__email', 'review_notes'
    ]
    readonly_fields = [
        'content_type', 'object_id', 'content_object_link',
        'ai_confidence', 'detected_issues_display', 'created_at', 'updated_at'
    ]
    fieldsets = [
        ('Contenu Signalé', {
            'fields': ('content_type_label', 'content_object_link', 'original_content', 'author')
        }),
        ('Analyse IA', {
            'fields': ('ai_confidence', 'detected_issues_display', 'severity')
        }),
        ('Statut de Modération', {
            'fields': ('status', 'auto_blocked')
        }),
        ('Révision Humaine', {
            'fields': ('reviewed_by', 'review_notes', 'review_date')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    ]
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def severity_badge(self, obj):
        colors = {
            'low': 'green',
            'medium': 'orange', 
            'high': 'red',
            'critical': 'darkred'
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Gravité'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'reviewing': 'blue',
            'approved': 'green',
            'rejected': 'red',
            'auto_filtered': 'purple'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def ai_confidence_display(self, obj):
        percentage = obj.ai_confidence * 100
        color = 'red' if percentage > 80 else 'orange' if percentage > 60 else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, percentage
        )
    ai_confidence_display.short_description = 'Confiance IA'
    
    def detected_issues_display(self, obj):
        if not obj.detected_issues:
            return "Aucun problème"
        
        issues_html = []
        for issue in obj.detected_issues:
            issue_type = issue.get('type', 'Inconnu')
            details = issue.get('details', '')
            rule = issue.get('rule', '')
            
            issues_html.append(
                f"<div style='margin-bottom: 5px;'>"
                f"<strong>{issue_type}</strong><br>"
                f"<small>Détails: {details}</small><br>"
                f"<small>Règle: {rule}</small>"
                f"</div>"
            )
        
        return format_html(''.join(issues_html))
    detected_issues_display.short_description = 'Problèmes Détectés'
    
    def content_object_link(self, obj):
        if obj.content_object:
            try:
                url = reverse(f'admin:{obj.content_type.app_label}_{obj.content_type.model}_change', 
                            args=[obj.object_id])
                return format_html('<a href="{}" target="_blank">Voir le contenu original</a>', url)
            except:
                return "Lien non disponible"
        return "Objet supprimé"
    content_object_link.short_description = 'Contenu Original'
    
    def review_actions(self, obj):
        if obj.status == 'pending':
            approve_url = reverse('admin:moderation_approve_report', args=[obj.id])
            reject_url = reverse('admin:moderation_reject_report', args=[obj.id])
            return format_html(
                '<a href="{}" style="color: green; margin-right: 10px;">✓ Approuver</a>'
                '<a href="{}" style="color: red;">✗ Rejeter</a>',
                approve_url, reject_url
            )
        return f"Révisé par {obj.reviewed_by}" if obj.reviewed_by else "-"
    review_actions.short_description = 'Actions'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('approve/<int:report_id>/', self.admin_site.admin_view(self.approve_report), 
                 name='moderation_approve_report'),
            path('reject/<int:report_id>/', self.admin_site.admin_view(self.reject_report),
                 name='moderation_reject_report'),
        ]
        return custom_urls + urls
    
    def approve_report(self, request, report_id):
        from django.shortcuts import redirect
        from django.contrib import messages
        
        success = moderator.review_report(report_id, request.user, 'approve', 
                                        "Approuvé via interface admin")
        if success:
            messages.success(request, "Rapport approuvé avec succès")
        else:
            messages.error(request, "Erreur lors de l'approbation")
        
        return redirect('admin:moderation_contentmoderationreport_changelist')
    
    def reject_report(self, request, report_id):
        from django.shortcuts import redirect
        from django.contrib import messages
        
        success = moderator.review_report(report_id, request.user, 'reject',
                                        "Rejeté via interface admin")
        if success:
            messages.success(request, "Rapport rejeté avec succès")
        else:
            messages.error(request, "Erreur lors du rejet")
        
        return redirect('admin:moderation_contentmoderationreport_changelist')


@admin.register(ContentModerationRule)
class ContentModerationRuleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'rule_type', 'severity_badge', 'threshold', 
        'auto_block', 'active', 'created_at'
    ]
    list_filter = ['rule_type', 'severity', 'auto_block', 'active']
    search_fields = ['name', 'description']
    fieldsets = [
        ('Règle de Base', {
            'fields': ('name', 'description', 'rule_type', 'active')
        }),
        ('Configuration', {
            'fields': ('keywords', 'patterns', 'threshold')
        }),
        ('Actions', {
            'fields': ('severity', 'auto_block')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    def severity_badge(self, obj):
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red', 
            'critical': 'darkred'
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Gravité'


@admin.register(ContentModerationWhitelist)
class ContentModerationWhitelistAdmin(admin.ModelAdmin):
    list_display = ['whitelist_type', 'value', 'description', 'active', 'created_by', 'created_at']
    list_filter = ['whitelist_type', 'active', 'created_at']
    search_fields = ['value', 'description']
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ModerationStats)
class ModerationStatsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_content_checked', 'flagged_content', 
        'flagged_percentage', 'auto_blocked', 'human_reviewed', 'false_positives'
    ]
    list_filter = ['date']
    readonly_fields = [
        'total_content_checked', 'flagged_content', 'auto_blocked',
        'human_reviewed', 'false_positives'
    ]
    date_hierarchy = 'date'
    ordering = ['-date']
    
    def flagged_percentage(self, obj):
        if obj.total_content_checked > 0:
            percentage = (obj.flagged_content / obj.total_content_checked) * 100
            color = 'red' if percentage > 10 else 'orange' if percentage > 5 else 'green'
            return format_html(
                '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
                color, percentage
            )
        return "0%"
    flagged_percentage.short_description = '% Signalé'
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation
    
    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion


# Custom admin site configuration
admin.site.site_header = "Modération de Contenu IA"
admin.site.site_title = "Modération IA"
admin.site.index_title = "Tableau de Bord de Modération"
