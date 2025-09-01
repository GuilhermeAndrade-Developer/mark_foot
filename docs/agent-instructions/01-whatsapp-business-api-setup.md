# WhatsApp Business API Setup

## Objective
Implement WhatsApp Business API integration for the Mark Foot football analytics chatbot.

## Current Project Context
- Django 4.2 backend with MySQL database
- Existing football data APIs (Football-Data.org, TheSportsDB)
- 8 AI/ML services already implemented
- Billing system with Stripe/PagSeguro/Mercado Pago
- Vue.js frontend for admin dashboard
- Celery + Redis for async tasks

## Technical Requirements

### 1. WhatsApp Business API Account Setup
- Create Meta Business Account
- Configure WhatsApp Business API
- Get phone number verification
- Set up webhook URL endpoint
- Configure webhook verification token

### 2. Backend Implementation

#### Create new Django app
```bash
cd services/web-service
python manage.py startapp whatsapp_integration
```

#### Models (whatsapp_integration/models.py)
```python
from django.db import models
from django.contrib.auth.models import User

class WhatsAppUser(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    is_premium = models.BooleanField(default=False)
    subscription_plan = models.CharField(max_length=20, default='free')
    daily_queries_count = models.IntegerField(default=0)
    last_query_date = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

class WhatsAppSession(models.Model):
    whatsapp_user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    context_data = models.JSONField(default=dict)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

class WhatsAppMessage(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('document', 'Document'),
        ('interactive', 'Interactive'),
    ]
    
    whatsapp_user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    message_id = models.CharField(max_length=100, unique=True)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    is_incoming = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
```

#### Views (whatsapp_integration/views.py)
```python
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import hashlib
import hmac
from .models import WhatsAppUser, WhatsAppMessage, WhatsAppSession
from .services import WhatsAppService, MessageProcessor

@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request):
    if request.method == "GET":
        # Webhook verification
        verify_token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")
        
        if verify_token == settings.WHATSAPP_VERIFY_TOKEN:
            return HttpResponse(challenge)
        return HttpResponse("Invalid verification token", status=403)
    
    elif request.method == "POST":
        # Process incoming message
        try:
            body = json.loads(request.body.decode('utf-8'))
            
            # Verify webhook signature
            if not verify_webhook_signature(request):
                return HttpResponse("Invalid signature", status=403)
            
            # Process message asynchronously
            process_whatsapp_message.delay(body)
            
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def verify_webhook_signature(request):
    signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
    if not signature:
        return False
    
    expected_signature = hmac.new(
        settings.WHATSAPP_APP_SECRET.encode('utf-8'),
        request.body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature[7:], expected_signature)
```

#### Services (whatsapp_integration/services.py)
```python
import requests
from django.conf import settings
from .models import WhatsAppUser, WhatsAppMessage, WhatsAppSession

class WhatsAppService:
    def __init__(self):
        self.api_url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_ID}/messages"
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
    
    def send_text_message(self, phone_number, message):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message}
        }
        
        response = requests.post(self.api_url, json=payload, headers=self.headers)
        return response.json()
    
    def send_interactive_message(self, phone_number, header, body, footer, buttons):
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
                    "buttons": buttons
                }
            }
        }
        
        response = requests.post(self.api_url, json=payload, headers=self.headers)
        return response.json()

class MessageProcessor:
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
    
    def process_incoming_message(self, message_data):
        # Extract message details
        phone_number = message_data['from']
        message_text = message_data.get('text', {}).get('body', '')
        message_id = message_data['id']
        
        # Get or create user
        user, created = WhatsAppUser.objects.get_or_create(
            phone_number=phone_number,
            defaults={'display_name': message_data.get('profile', {}).get('name', '')}
        )
        
        # Save message
        WhatsAppMessage.objects.create(
            whatsapp_user=user,
            message_id=message_id,
            message_type='text',
            content=message_text,
            is_incoming=True
        )
        
        # Check rate limits
        if not self.check_rate_limits(user):
            self.send_rate_limit_message(phone_number)
            return
        
        # Process message through NLP and generate response
        response = self.generate_response(message_text, user)
        self.whatsapp_service.send_text_message(phone_number, response)
    
    def check_rate_limits(self, user):
        if user.is_premium:
            return True
        
        from datetime import date
        today = date.today()
        
        if user.last_query_date != today:
            user.daily_queries_count = 0
            user.last_query_date = today
            user.save()
        
        if user.daily_queries_count >= 5:  # Free tier limit
            return False
        
        user.daily_queries_count += 1
        user.save()
        return True
    
    def generate_response(self, message_text, user):
        # Integrate with existing AI services
        from ai_analytics.services import FootballAnalyticsService
        
        analytics_service = FootballAnalyticsService()
        
        # Simple intent recognition (to be enhanced with proper NLP)
        message_lower = message_text.lower()
        
        if any(word in message_lower for word in ['flamengo', 'palmeiras', 'time']):
            return analytics_service.get_team_stats_summary(message_text)
        elif any(word in message_lower for word in ['odds', 'aposta', 'cotacao']):
            return "Análise de odds disponível apenas para usuários Premium. Digite /premium para saber mais."
        elif message_lower.startswith('/premium'):
            return self.get_premium_message()
        else:
            return "Olá! Sou o Mark Foot Bot. Posso ajudar com estatísticas de futebol. Digite o nome de um time ou jogador para começar."
    
    def get_premium_message(self):
        return """
🏆 Mark Foot Premium

✅ Consultas ilimitadas
✅ Análise completa de odds
✅ Previsões com IA
✅ Alertas personalizados

💰 Apenas R$ 19,90/mês

Para assinar: [LINK_PAGAMENTO]
        """.strip()
```

#### Celery Tasks (whatsapp_integration/tasks.py)
```python
from celery import shared_task
from .services import MessageProcessor

@shared_task(bind=True, max_retries=3)
def process_whatsapp_message(self, webhook_data):
    try:
        processor = MessageProcessor()
        
        if 'entry' in webhook_data:
            for entry in webhook_data['entry']:
                if 'changes' in entry:
                    for change in entry['changes']:
                        if change['field'] == 'messages':
                            if 'messages' in change['value']:
                                for message in change['value']['messages']:
                                    processor.process_incoming_message(message)
        
    except Exception as exc:
        self.retry(countdown=60, exc=exc)
```

### 3. Settings Configuration

#### Add to settings.py
```python
# WhatsApp Configuration
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
WHATSAPP_PHONE_ID = os.getenv('WHATSAPP_PHONE_ID')
WHATSAPP_APP_SECRET = os.getenv('WHATSAPP_APP_SECRET')
WHATSAPP_VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN')

INSTALLED_APPS = [
    # ... existing apps
    'whatsapp_integration',
]
```

#### Environment Variables (.env)
```
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_PHONE_ID=your_phone_id
WHATSAPP_APP_SECRET=your_app_secret
WHATSAPP_VERIFY_TOKEN=your_verify_token
```

### 4. URL Configuration

#### whatsapp_integration/urls.py
```python
from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.webhook, name='whatsapp_webhook'),
]
```

#### Add to main urls.py
```python
urlpatterns = [
    # ... existing patterns
    path('whatsapp/', include('whatsapp_integration.urls')),
]
```

### 5. Database Migration
```bash
python manage.py makemigrations whatsapp_integration
python manage.py migrate
```

### 6. Testing Setup

#### Create test webhook endpoint
```python
# For development testing
@csrf_exempt
def test_webhook(request):
    if request.method == "POST":
        print("Received webhook:", request.body.decode())
        return JsonResponse({"status": "received"})
    return JsonResponse({"error": "Method not allowed"}, status=405)
```

## Integration Points

### Connect to Existing Services
1. Use existing AI analytics services from ai_analytics app
2. Integrate with billing system for premium subscriptions
3. Leverage existing football data from core models
4. Extend Celery task system for message processing

### Rate Limiting Integration
- Free users: 5 queries per day
- Premium users: Unlimited queries
- Use existing billing models to check subscription status

## Expected Deliverables

1. WhatsApp Business API webhook endpoint
2. Message processing pipeline
3. User management for WhatsApp users
4. Rate limiting implementation
5. Basic NLP for football queries
6. Integration with existing AI services
7. Premium subscription flow
8. Admin interface for WhatsApp management

## Testing Requirements

1. Webhook verification working
2. Message sending/receiving functional
3. Rate limiting enforced
4. Premium user detection working
5. Integration with existing football data
6. Error handling and logging

## Success Criteria

- Webhook receives and processes messages correctly
- Users can query football statistics via WhatsApp
- Rate limiting prevents abuse
- Premium users get enhanced features
- System integrates seamlessly with existing backend
- Response time under 2 seconds for simple queries
