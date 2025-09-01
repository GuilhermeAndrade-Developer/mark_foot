# Backward compatibility imports
from .services.whatsapp_service import WhatsAppService
from .services.message_processor import MessageProcessor
from .services.subscription_service import WhatsAppSubscriptionService

# Re-export for backward compatibility
__all__ = ['WhatsAppService', 'MessageProcessor', 'WhatsAppSubscriptionService']
