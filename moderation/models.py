from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from users.models import Utilisateur
import re
import json


class ContentModerationReport(models.Model):
    """Track inappropriate content detection and moderation actions"""
    
    SEVERITY_CHOICES = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('critical', 'Critique'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('reviewing', 'En révision'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
        ('auto_filtered', 'Filtré automatiquement'),
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('course_comment', 'Commentaire de cours'),
        ('discussion_reply', 'Réponse de discussion'),
        ('group_message', 'Message de groupe'),
        ('private_message', 'Message privé'),
        ('formation_comment', 'Commentaire de formation'),
        ('task_description', 'Description de tâche'),
    ]
    
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Moderation details
    content_type_label = models.CharField(max_length=50, choices=CONTENT_TYPE_CHOICES)
    original_content = models.TextField(help_text="Contenu original signalé")
    author = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='moderation_reports')
    
    # AI Analysis results
    ai_confidence = models.FloatField(help_text="Confiance de l'IA (0.0 - 1.0)")
    detected_issues = models.JSONField(default=list, help_text="Liste des problèmes détectés")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    
    # Moderation status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    auto_blocked = models.BooleanField(default=False, help_text="Contenu bloqué automatiquement")
    
    # Human review
    reviewed_by = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderation_reviews')
    review_notes = models.TextField(blank=True, help_text="Notes du modérateur")
    review_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Rapport de Modération'
        verbose_name_plural = 'Rapports de Modération'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['auto_blocked']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"Modération {self.content_type_label} - {self.severity} ({self.status})"
    
    @property
    def issues_display(self):
        """Human-readable list of detected issues"""
        if not self.detected_issues:
            return "Aucun problème détecté"
        return ", ".join([issue.get('type', 'Inconnu') for issue in self.detected_issues])


class ContentModerationRule(models.Model):
    """Define rules for content moderation"""
    
    RULE_TYPE_CHOICES = [
        ('keyword', 'Mots-clés'),
        ('pattern', 'Expressions régulières'),
        ('sentiment', 'Analyse de sentiment'),
        ('toxicity', 'Détection de toxicité'),
        ('spam', 'Détection de spam'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES)
    
    # Rule configuration
    keywords = models.JSONField(default=list, blank=True, help_text="Liste de mots-clés à détecter")
    patterns = models.JSONField(default=list, blank=True, help_text="Expressions régulières")
    threshold = models.FloatField(default=0.5, help_text="Seuil de détection (0.0 - 1.0)")
    
    # Action configuration
    auto_block = models.BooleanField(default=False, help_text="Bloquer automatiquement le contenu")
    severity = models.CharField(max_length=20, choices=ContentModerationReport.SEVERITY_CHOICES, default='medium')
    
    # Metadata
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Règle de Modération'
        verbose_name_plural = 'Règles de Modération'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.rule_type})"
    
    def check_content(self, content):
        """Check if content violates this rule"""
        if not self.active or not content:
            return False, 0.0, []
        
        issues = []
        confidence = 0.0
        
        if self.rule_type == 'keyword':
            confidence, detected_keywords = self._check_keywords(content)
            if detected_keywords:
                issues.append({
                    'type': 'Mots-clés inappropriés',
                    'details': detected_keywords,
                    'rule': self.name
                })
        
        elif self.rule_type == 'pattern':
            confidence, detected_patterns = self._check_patterns(content)
            if detected_patterns:
                issues.append({
                    'type': 'Contenu inapproprié détecté',
                    'details': detected_patterns,
                    'rule': self.name
                })
        
        elif self.rule_type == 'sentiment':
            confidence = self._analyze_sentiment(content)
            if confidence >= self.threshold:
                issues.append({
                    'type': 'Sentiment négatif',
                    'details': f'Score: {confidence:.2f}',
                    'rule': self.name
                })
        
        elif self.rule_type == 'toxicity':
            confidence = self._analyze_toxicity(content)
            if confidence >= self.threshold:
                issues.append({
                    'type': 'Contenu toxique',
                    'details': f'Score: {confidence:.2f}',
                    'rule': self.name
                })
        
        elif self.rule_type == 'spam':
            confidence = self._detect_spam(content)
            if confidence >= self.threshold:
                issues.append({
                    'type': 'Spam détecté',
                    'details': f'Score: {confidence:.2f}',
                    'rule': self.name
                })
        
        return confidence >= self.threshold, confidence, issues
    
    def _check_keywords(self, content):
        """Check for inappropriate keywords"""
        if not self.keywords:
            return 0.0, []
        
        content_lower = content.lower()
        detected = []
        
        for keyword in self.keywords:
            if keyword.lower() in content_lower:
                detected.append(keyword)
        
        confidence = len(detected) / len(self.keywords) if self.keywords else 0.0
        return confidence, detected
    
    def _check_patterns(self, content):
        """Check for regex patterns"""
        if not self.patterns:
            return 0.0, []
        
        detected = []
        
        for pattern in self.patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    detected.extend(matches)
            except re.error:
                continue
        
        confidence = 1.0 if detected else 0.0
        return confidence, detected
    
    def _analyze_sentiment(self, content):
        """Simple sentiment analysis (can be enhanced with AI libraries)"""
        # Simple negative sentiment detection
        negative_words = [
            'nul', 'terrible', 'horreur', 'déteste', 'stupide', 'idiot',
            'débile', 'merde', 'pourri', 'catastrophe', 'disaster'
        ]
        
        content_lower = content.lower()
        negative_count = sum(1 for word in negative_words if word in content_lower)
        total_words = len(content.split())
        
        return min(negative_count / max(total_words * 0.1, 1), 1.0)
    
    def _analyze_toxicity(self, content):
        """Simple toxicity detection (can be enhanced with AI libraries)"""
        toxic_patterns = [
            r'\b(?:con+ard|sal[eo]pe?|put[ea]|merde|chier|foutre)\b',
            r'\b(?:ferme\s+ta\s+gueule|va\s+te\s+faire)\b',
            r'(?:espèce\s+de?|sale)\s+(?:con|idiot|débile)',
        ]
        
        for pattern in toxic_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return 1.0
        
        return 0.0
    
    def _detect_spam(self, content):
        """Simple spam detection"""
        spam_indicators = [
            r'(?:https?://|www\.)\S+',  # URLs
            r'(?:achetez|vendez|gratuit|promotion|offre\s+spéciale)',  # Commercial
            r'(?:contactez|appelez|envoyez|email)',  # Contact requests
            r'[A-Z\s]{20,}',  # All caps spam
            r'(.)\1{4,}',  # Repeated characters
        ]
        
        score = 0.0
        for pattern in spam_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                score += 0.3
        
        return min(score, 1.0)


class ContentModerationWhitelist(models.Model):
    """Whitelist for approved content or users"""
    
    WHITELIST_TYPE_CHOICES = [
        ('user', 'Utilisateur'),
        ('keyword', 'Mot-clé'),
        ('domain', 'Domaine'),
        ('phrase', 'Phrase'),
    ]
    
    whitelist_type = models.CharField(max_length=20, choices=WHITELIST_TYPE_CHOICES)
    value = models.CharField(max_length=200, help_text="Valeur à autoriser")
    description = models.TextField(blank=True)
    
    active = models.BooleanField(default=True)
    created_by = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Liste Blanche'
        verbose_name_plural = 'Listes Blanches'
        unique_together = ['whitelist_type', 'value']
    
    def __str__(self):
        return f"{self.whitelist_type}: {self.value}"


class ModerationStats(models.Model):
    """Track moderation statistics"""
    
    date = models.DateField(unique=True, default=timezone.now)
    total_content_checked = models.PositiveIntegerField(default=0)
    flagged_content = models.PositiveIntegerField(default=0)
    auto_blocked = models.PositiveIntegerField(default=0)
    human_reviewed = models.PositiveIntegerField(default=0)
    false_positives = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Statistiques de Modération'
        verbose_name_plural = 'Statistiques de Modération'
        ordering = ['-date']
    
    def __str__(self):
        return f"Stats {self.date}: {self.flagged_content}/{self.total_content_checked} signalés"
