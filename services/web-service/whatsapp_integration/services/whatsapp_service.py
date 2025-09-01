import requests
import json
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for sending messages via WhatsApp Business API"""
    
    def __init__(self):
        self.api_url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_ID}/messages"
        self.headers = {
            'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
    
    def send_text_message(self, phone_number, message):
        """Send a text message"""
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            raise
    
    def send_interactive_message(self, phone_number, header, body, footer, buttons):
        """Send an interactive message with buttons"""
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "header": {"type": "text", "text": header},
                "body": {"text": body},
                "footer": {"text": footer},
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {"id": btn["id"], "title": btn["title"]}
                        } for btn in buttons
                    ]
                }
            }
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error sending WhatsApp interactive message: {str(e)}")
            raise

    def send_premium_promotion(self, phone_number):
        """Send premium subscription promotion"""
        message = """
🏆 Mark Foot Premium

✅ Consultas ilimitadas
✅ Análise completa de odds
✅ Previsões com IA
✅ Alertas personalizados
✅ Estatísticas avançadas

💰 Apenas R$ 19,90/mês

Para assinar: Digite *PREMIUM* ou acesse nosso site
        """.strip()
        
        return self.send_text_message(phone_number, message)
