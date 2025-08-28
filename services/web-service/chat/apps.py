"""
Chat application configuration.
"""

from django.apps import AppConfig


class ChatConfig(AppConfig):
    """Configuration for the Chat app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'
    verbose_name = 'Live Chat'
    
    def ready(self):
        """App ready hook for importing signals."""
        try:
            import chat.signals  # noqa F401
        except ImportError:
            pass
