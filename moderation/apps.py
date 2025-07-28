from django.apps import AppConfig


class ModerationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'moderation'
    verbose_name = 'Modération de Contenu IA'
    
    def ready(self):
        """Connect signal handlers when app is ready"""
        import moderation.signals
