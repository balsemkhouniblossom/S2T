from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Formation, Salle, Planning, Presence, Evaluation, Attestation, TrainerApplication, Task


class TrainerApplicationInline(admin.TabularInline):
    """Inline for managing trainer applications within formation admin"""
    model = TrainerApplication
    extra = 0
    fields = ('formateur', 'statut', 'tarif_propose', 'date_candidature')
    readonly_fields = ('formateur', 'date_candidature')
    ordering = ('-date_candidature',)


class PlanningInline(admin.TabularInline):
    """Inline for managing sessions within formation admin"""
    model = Planning
    extra = 1
    fields = ('salle', 'date_session', 'duree_session', 'sujet', 'description', 'code_presence')
    ordering = ('date_session',)


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'formateur', 'niveau', 'prix', 'statut', 'applications_ouvertes', 'applications_count_display', 'participants_inscrits', 'sessions_count', 'date_debut')
    list_filter = ('niveau', 'statut', 'applications_ouvertes', 'date_creation', 'formateur')
    search_fields = ('titre', 'formateur__utilisateur__nom', 'formateur__utilisateur__prenom')
    date_hierarchy = 'date_debut'
    inlines = [TrainerApplicationInline, PlanningInline]
    filter_horizontal = ('participants',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'description', 'objectifs', 'formateur')
        }),
        ('Détails formation', {
            'fields': ('niveau', 'duree_heures', 'prix', 'participants_max', 'prerequisites')
        }),
        ('Candidatures formateurs', {
            'fields': ('applications_ouvertes', 'date_limite_candidature'),
            'description': 'Paramètres pour permettre aux formateurs de candidater'
        }),
        ('Planification', {
            'fields': ('date_debut', 'date_fin', 'statut')
        }),
        ('Participants', {
            'fields': ('participants',),
            'classes': ('collapse',)
        })
    )
    
    def applications_count_display(self, obj):
        count = obj.applications_count
        if count > 0:
            pending = obj.pending_applications_count
            if pending > 0:
                return format_html('<span style="color: orange; font-weight: bold;">{} candidatures ({} en attente)</span>', count, pending)
            return format_html('<span style="color: green;">{} candidatures</span>', count)
        return '0 candidatures'
    applications_count_display.short_description = 'Candidatures'
    
    def participants_inscrits(self, obj):
        return obj.participants_inscrits
    participants_inscrits.short_description = 'Inscrits'
    
    def sessions_count(self, obj):
        count = obj.sessions.count()
        if count > 0:
            url = reverse('admin:formations_planning_changelist') + f'?formation__id__exact={obj.id}'
            return format_html('<a href="{}">{} sessions</a>', url, count)
        return '0 sessions'
    sessions_count.short_description = 'Sessions'


@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'capacite', 'localisation', 'disponible', 'sessions_today')
    list_filter = ('disponible', 'capacite')
    search_fields = ('nom', 'localisation')
    list_editable = ('disponible',)
    
    def sessions_today(self, obj):
        today = timezone.now().date()
        count = obj.planning_set.filter(date_session__date=today).count()
        if count > 0:
            return format_html('<span style="color: red;">{} sessions aujourd\'hui</span>', count)
        return 'Libre'
    sessions_today.short_description = 'Aujourd\'hui'


@admin.register(Planning)
class PlanningAdmin(admin.ModelAdmin):
    list_display = ('formation_link', 'salle', 'date_session', 'duree_minutes', 'sujet', 'participants_count', 'status')
    list_filter = ('date_session', 'salle', 'formation__statut', 'formation__formateur')
    search_fields = ('formation__titre', 'sujet', 'salle__nom')
    date_hierarchy = 'date_session'
    raw_id_fields = ('formation',)
    
    fieldsets = (
        ('Session', {
            'fields': ('formation', 'salle', 'sujet', 'description')
        }),
        ('Planification', {
            'fields': ('date_session', 'duree_session', 'code_presence')
        })
    )
    
    def formation_link(self, obj):
        url = reverse('admin:formations_formation_change', args=[obj.formation.id])
        return format_html('<a href="{}">{}</a>', url, obj.formation.titre)
    formation_link.short_description = 'Formation'
    
    def duree_minutes(self, obj):
        hours, remainder = divmod(obj.duree_session, 60)
        if hours > 0:
            return f"{hours}h {remainder}min"
        return f"{remainder}min"
    duree_minutes.short_description = 'Durée'
    
    def participants_count(self, obj):
        return obj.formation.participants_inscrits
    participants_count.short_description = 'Participants'
    
    def status(self, obj):
        now = timezone.now()
        session_end = obj.date_session + timezone.timedelta(minutes=obj.duree_session)
        
        if now < obj.date_session:
            return format_html('<span style="color: blue;">À venir</span>')
        elif obj.date_session <= now <= session_end:
            return format_html('<span style="color: green;">En cours</span>')
        else:
            return format_html('<span style="color: gray;">Terminée</span>')
    status.short_description = 'Statut'


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ('planning_info', 'apprenant', 'present', 'heure_arrivee', 'duree_presence')
    list_filter = ('present', 'planning__date_session', 'planning__formation')
    search_fields = ('apprenant__utilisateur__nom', 'apprenant__utilisateur__prenom', 'planning__formation__titre')
    date_hierarchy = 'planning__date_session'
    list_editable = ('present',)
    
    def planning_info(self, obj):
        return f"{obj.planning.formation.titre} - {obj.planning.date_session.strftime('%d/%m/%Y %H:%M')}"
    planning_info.short_description = 'Session'
    
    def duree_presence(self, obj):
        if obj.heure_arrivee and obj.heure_depart:
            duree = obj.heure_depart - obj.heure_arrivee
            return f"{duree.total_seconds() // 3600:.0f}h {(duree.total_seconds() % 3600) // 60:.0f}min"
        return '-'
    duree_presence.short_description = 'Durée présence'


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('formation', 'apprenant', 'note_globale', 'moyenne_notes', 'recommande', 'date_evaluation')
    list_filter = ('note_globale', 'recommande', 'date_evaluation', 'formation')
    search_fields = ('formation__titre', 'apprenant__utilisateur__nom', 'apprenant__utilisateur__prenom')
    readonly_fields = ('moyenne_notes',)
    
    fieldsets = (
        ('Participant', {
            'fields': ('formation', 'apprenant')
        }),
        ('Évaluation détaillée', {
            'fields': ('note_contenu', 'note_formateur', 'note_organisation', 'note_globale', 'moyenne_notes')
        }),
        ('Commentaires', {
            'fields': ('commentaire', 'recommande')
        })
    )
    
    def moyenne_notes(self, obj):
        if obj.pk:
            moyenne = (obj.note_contenu + obj.note_formateur + obj.note_organisation) / 3
            return f"{moyenne:.1f}/5"
        return '-'
    moyenne_notes.short_description = 'Moyenne détaillée'


@admin.register(Attestation)
class AttestationAdmin(admin.ModelAdmin):
    list_display = ('numero_attestation', 'formation', 'apprenant', 'note_obtenue', 'date_emission', 'has_pdf')
    list_filter = ('date_emission', 'formation')
    search_fields = ('numero_attestation', 'formation__titre', 'apprenant__utilisateur__nom', 'apprenant__utilisateur__prenom')
    readonly_fields = ('numero_attestation', 'date_emission')
    
    def has_pdf(self, obj):
        if obj.fichier_pdf:
            return format_html('<a href="{}" target="_blank">📄 Télécharger</a>', obj.fichier_pdf.url)
        return format_html('<span style="color: red;">Pas de PDF</span>')
    has_pdf.short_description = 'Fichier PDF'
    
    def save_model(self, request, obj, form, change):
        if not obj.numero_attestation:
            # Generate unique attestation number
            import uuid
            obj.numero_attestation = f"ATT-{uuid.uuid4().hex[:8].upper()}"
        super().save_model(request, obj, form, change)


@admin.register(TrainerApplication)
class TrainerApplicationAdmin(admin.ModelAdmin):
    list_display = ('formateur_name', 'formation_title', 'statut', 'tarif_propose', 'date_candidature', 'date_reponse')
    list_filter = ('statut', 'date_candidature', 'formation__niveau')
    search_fields = ('formateur__utilisateur__nom', 'formateur__utilisateur__prenom', 'formation__titre')
    readonly_fields = ('date_candidature',)
    date_hierarchy = 'date_candidature'
    
    fieldsets = (
        ('Candidature', {
            'fields': ('formation', 'formateur', 'statut', 'date_candidature')
        }),
        ('Détails de la candidature', {
            'fields': ('motivation', 'experience_pertinente', 'tarif_propose', 'disponibilite', 'message')
        }),
        ('Réponse administrative', {
            'fields': ('commentaire_admin', 'date_reponse'),
            'classes': ('collapse',)
        })
    )
    
    def formateur_name(self, obj):
        return obj.formateur.utilisateur.get_full_name()
    formateur_name.short_description = 'Formateur'
    
    def formation_title(self, obj):
        return obj.formation.titre
    formation_title.short_description = 'Formation'
    
    def save_model(self, request, obj, form, change):
        if change and 'statut' in form.changed_data:
            obj.date_reponse = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'titre', 'createur', 'statut', 'priorite', 'categorie',
        'date_creation', 'date_echeance', 'is_overdue_display'
    ]
    list_filter = [
        'statut', 'priorite', 'categorie', 'date_creation',
        'date_echeance'
    ]
    search_fields = ['titre', 'description', 'createur__nom', 'createur__prenom', 'createur__email']
    readonly_fields = ['date_creation', 'date_modification', 'date_completion']
    date_hierarchy = 'date_creation'
    ordering = ('-date_creation',)
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('createur', 'titre', 'description', 'categorie')
        }),
        ('Statut et priorité', {
            'fields': ('statut', 'priorite')
        }),
        ('Dates', {
            'fields': ('date_echeance', 'date_creation', 'date_modification', 'date_completion')
        }),
        ('Liaisons', {
            'fields': ('formation_liee',),
            'classes': ('collapse',)
        }),
        ('Détails supplémentaires', {
            'fields': ('notes', 'fichiers_attaches'),
            'classes': ('collapse',)
        }),
    )
    
    def is_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">Oui</span>')
        return format_html('<span style="color: green;">Non</span>')
    is_overdue_display.short_description = 'En retard'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('createur', 'formation_liee')


# Custom admin site configuration
admin.site.site_header = "Administration - Système de Gestion de Formation"
admin.site.site_title = "Admin Formation"
admin.site.index_title = "Tableau de bord administrateur"
