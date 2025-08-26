from django.apps import AppConfig


class GamificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gamification'
    verbose_name = 'Sistema de Gamificação'
    
    def ready(self):
        """Carrega signals quando o app é inicializado"""
        import gamification.signals  # noqa
