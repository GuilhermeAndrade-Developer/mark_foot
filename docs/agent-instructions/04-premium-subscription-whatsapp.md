# Premium Subscription Integration with WhatsApp

## Objective
Integrate the existing billing system with WhatsApp chatbot to enable seamless premium subscription management, payment processing, and feature access control.

## Current Project Context
- Existing billing app with Stripe, PagSeguro, Mercado Pago
- WhatsApp integration with user management
- NLP engine for intent recognition
- Premium/free tier functionality requirements
- Vue.js admin dashboard for subscription management

## Technical Requirements

### 1. Extend WhatsApp User Model

#### Update whatsapp_integration/models.py
```python
from django.db import models
from django.contrib.auth.models import User
from billing.models import Subscription, Plan

class WhatsAppUser(models.Model):
    SUBSCRIPTION_STATUS = [
        ('free', 'Free'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    phone_number = models.CharField(max_length=20, unique=True)
    display_name = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Subscription information
    subscription_status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='free')
    current_plan = models.ForeignKey(Plan, null=True, blank=True, on_delete=models.SET_NULL)
    subscription = models.ForeignKey(Subscription, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Usage tracking
    daily_queries_count = models.IntegerField(default=0)
    monthly_queries_count = models.IntegerField(default=0)
    last_query_date = models.DateField(auto_now=True)
    last_reset_date = models.DateField(auto_now_add=True)
    
    # Premium features tracking
    premium_activated_date = models.DateTimeField(null=True, blank=True)
    trial_used = models.BooleanField(default=False)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    
    # Payment tracking
    payment_customer_id = models.CharField(max_length=100, blank=True)  # Stripe/PagSeguro customer ID
    payment_method_default = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def is_premium(self):
        return self.subscription_status in ['premium', 'pro']
    
    @property
    def can_use_premium_features(self):
        if self.is_premium:
            return True
        # Check if in trial period
        if self.trial_end_date and timezone.now() < self.trial_end_date:
            return True
        return False
    
    @property
    def daily_limit(self):
        if self.is_premium:
            return None  # Unlimited
        return 5  # Free tier limit
    
    @property
    def monthly_limit(self):
        if self.subscription_status == 'pro':
            return None  # Unlimited
        elif self.subscription_status == 'premium':
            return 1000  # Premium limit
        return 50  # Free tier limit

class WhatsAppPaymentIntent(models.Model):
    whatsapp_user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    payment_intent_id = models.CharField(max_length=200)
    payment_provider = models.CharField(max_length=50)  # stripe, pagseguro, mercadopago
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='BRL')
    status = models.CharField(max_length=50, default='pending')
    payment_url = models.URLField(blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
class WhatsAppSubscriptionEvent(models.Model):
    EVENT_TYPES = [
        ('subscription_created', 'Subscription Created'),
        ('subscription_activated', 'Subscription Activated'),
        ('subscription_cancelled', 'Subscription Cancelled'),
        ('subscription_expired', 'Subscription Expired'),
        ('payment_successful', 'Payment Successful'),
        ('payment_failed', 'Payment Failed'),
        ('trial_started', 'Trial Started'),
        ('trial_ended', 'Trial Ended'),
    ]
    
    whatsapp_user = models.ForeignKey(WhatsAppUser, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 2. Subscription Service for WhatsApp

#### whatsapp_integration/services/subscription_service.py
```python
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from billing.services import StripeService, PagSeguroService, MercadoPagoService
from billing.models import Plan, Subscription
from ..models import WhatsAppUser, WhatsAppPaymentIntent, WhatsAppSubscriptionEvent

class WhatsAppSubscriptionService:
    def __init__(self):
        self.stripe_service = StripeService()
        self.pagseguro_service = PagSeguroService()
        self.mercadopago_service = MercadoPagoService()
    
    def create_subscription_payment_link(self, whatsapp_user, plan_name, payment_method='auto'):
        """Create payment link for subscription"""
        plan = Plan.objects.get(name=plan_name)
        
        # Choose payment provider based on method or user preference
        if payment_method == 'auto':
            payment_method = self._determine_best_payment_method(whatsapp_user)
        
        try:
            if payment_method == 'stripe':
                result = self._create_stripe_payment_link(whatsapp_user, plan)
            elif payment_method == 'pagseguro':
                result = self._create_pagseguro_payment_link(whatsapp_user, plan)
            elif payment_method == 'mercadopago':
                result = self._create_mercadopago_payment_link(whatsapp_user, plan)
            else:
                raise ValueError(f"Unsupported payment method: {payment_method}")
            
            # Save payment intent
            payment_intent = WhatsAppPaymentIntent.objects.create(
                whatsapp_user=whatsapp_user,
                plan=plan,
                payment_intent_id=result['payment_id'],
                payment_provider=payment_method,
                amount=plan.price,
                payment_url=result['payment_url'],
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            return {
                'success': True,
                'payment_url': result['payment_url'],
                'payment_id': result['payment_id'],
                'expires_in': '24 horas'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _determine_best_payment_method(self, whatsapp_user):
        """Determine best payment method based on user location/preferences"""
        # For Brazilian users, prefer PagSeguro/Mercado Pago
        # For international users, prefer Stripe
        if whatsapp_user.phone_number.startswith('+55'):  # Brazil
            return 'pagseguro'
        else:
            return 'stripe'
    
    def _create_stripe_payment_link(self, whatsapp_user, plan):
        """Create Stripe subscription payment link"""
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Create or get customer
        customer_data = {
            'phone': whatsapp_user.phone_number,
            'metadata': {
                'whatsapp_user_id': whatsapp_user.id,
                'source': 'whatsapp'
            }
        }
        
        if whatsapp_user.payment_customer_id:
            customer = stripe.Customer.retrieve(whatsapp_user.payment_customer_id)
        else:
            customer = stripe.Customer.create(**customer_data)
            whatsapp_user.payment_customer_id = customer.id
            whatsapp_user.save()
        
        # Create payment link
        payment_link = stripe.PaymentLink.create(
            line_items=[{
                'price': plan.stripe_price_id,
                'quantity': 1,
            }],
            metadata={
                'whatsapp_user_id': whatsapp_user.id,
                'plan_id': plan.id,
            },
            after_completion={
                'type': 'redirect',
                'redirect': {
                    'url': f"{settings.FRONTEND_URL}/subscription/success"
                }
            }
        )
        
        return {
            'payment_id': payment_link.id,
            'payment_url': payment_link.url
        }
    
    def _create_pagseguro_payment_link(self, whatsapp_user, plan):
        """Create PagSeguro payment link"""
        payment_data = {
            'reference_id': f"whatsapp_{whatsapp_user.id}_{plan.id}",
            'customer': {
                'name': whatsapp_user.display_name or 'Usuario WhatsApp',
                'email': f"user{whatsapp_user.id}@markfoot.com",  # Temporary email
                'phone': whatsapp_user.phone_number,
            },
            'items': [{
                'reference_id': plan.id,
                'name': f"Mark Foot {plan.name}",
                'quantity': 1,
                'unit_amount': int(plan.price * 100)  # Convert to cents
            }],
            'qr_codes': [{'amount': {'value': int(plan.price * 100)}}],
            'notification_urls': [f"{settings.BACKEND_URL}/webhooks/pagseguro/"]
        }
        
        response = self.pagseguro_service.create_order(payment_data)
        
        return {
            'payment_id': response['id'],
            'payment_url': response['links'][0]['href']  # Payment link
        }
    
    def _create_mercadopago_payment_link(self, whatsapp_user, plan):
        """Create Mercado Pago payment link"""
        preference_data = {
            'items': [{
                'title': f"Mark Foot {plan.name}",
                'quantity': 1,
                'unit_price': float(plan.price),
                'currency_id': 'BRL'
            }],
            'payer': {
                'phone': {'number': whatsapp_user.phone_number},
                'name': whatsapp_user.display_name or 'Usuario WhatsApp'
            },
            'external_reference': f"whatsapp_{whatsapp_user.id}_{plan.id}",
            'notification_url': f"{settings.BACKEND_URL}/webhooks/mercadopago/",
            'back_urls': {
                'success': f"{settings.FRONTEND_URL}/subscription/success",
                'failure': f"{settings.FRONTEND_URL}/subscription/failure",
                'pending': f"{settings.FRONTEND_URL}/subscription/pending"
            }
        }
        
        response = self.mercadopago_service.create_preference(preference_data)
        
        return {
            'payment_id': response['id'],
            'payment_url': response['init_point']
        }
    
    def process_successful_payment(self, payment_intent_id, payment_provider):
        """Process successful payment and activate subscription"""
        try:
            payment_intent = WhatsAppPaymentIntent.objects.get(
                payment_intent_id=payment_intent_id,
                payment_provider=payment_provider
            )
            
            whatsapp_user = payment_intent.whatsapp_user
            plan = payment_intent.plan
            
            # Create subscription record
            subscription = Subscription.objects.create(
                user=whatsapp_user.user,
                plan=plan,
                status='active',
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=30)  # Monthly subscription
            )
            
            # Update WhatsApp user
            whatsapp_user.subscription = subscription
            whatsapp_user.current_plan = plan
            whatsapp_user.subscription_status = plan.name.lower()
            whatsapp_user.premium_activated_date = timezone.now()
            whatsapp_user.save()
            
            # Log event
            WhatsAppSubscriptionEvent.objects.create(
                whatsapp_user=whatsapp_user,
                event_type='subscription_activated',
                event_data={
                    'plan': plan.name,
                    'payment_provider': payment_provider,
                    'payment_intent_id': payment_intent_id
                }
            )
            
            # Update payment intent status
            payment_intent.status = 'completed'
            payment_intent.save()
            
            return {
                'success': True,
                'subscription_id': subscription.id,
                'message': 'Assinatura ativada com sucesso!'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def start_free_trial(self, whatsapp_user, trial_days=7):
        """Start free trial for user"""
        if whatsapp_user.trial_used:
            return {
                'success': False,
                'message': 'Trial já foi utilizado'
            }
        
        whatsapp_user.trial_used = True
        whatsapp_user.trial_end_date = timezone.now() + timedelta(days=trial_days)
        whatsapp_user.subscription_status = 'premium'  # Trial gives premium access
        whatsapp_user.save()
        
        # Log event
        WhatsAppSubscriptionEvent.objects.create(
            whatsapp_user=whatsapp_user,
            event_type='trial_started',
            event_data={'trial_days': trial_days}
        )
        
        return {
            'success': True,
            'trial_end_date': whatsapp_user.trial_end_date,
            'message': f'Trial de {trial_days} dias ativado!'
        }
    
    def cancel_subscription(self, whatsapp_user):
        """Cancel user subscription"""
        if not whatsapp_user.subscription:
            return {
                'success': False,
                'message': 'Nenhuma assinatura ativa encontrada'
            }
        
        # Cancel in payment provider
        if whatsapp_user.subscription.status == 'active':
            # Cancel recurring payment
            subscription = whatsapp_user.subscription
            subscription.status = 'cancelled'
            subscription.save()
            
            # Update WhatsApp user
            whatsapp_user.subscription_status = 'cancelled'
            whatsapp_user.save()
            
            # Log event
            WhatsAppSubscriptionEvent.objects.create(
                whatsapp_user=whatsapp_user,
                event_type='subscription_cancelled',
                event_data={'cancelled_date': timezone.now().isoformat()}
            )
            
            return {
                'success': True,
                'message': 'Assinatura cancelada. Acesso premium mantido até o final do período pago.'
            }
        
        return {
            'success': False,
            'message': 'Assinatura não pode ser cancelada'
        }
    
    def check_subscription_status(self, whatsapp_user):
        """Check and update subscription status"""
        if whatsapp_user.subscription:
            subscription = whatsapp_user.subscription
            
            # Check if subscription expired
            if subscription.end_date < timezone.now():
                if subscription.status == 'active':
                    subscription.status = 'expired'
                    subscription.save()
                    
                    whatsapp_user.subscription_status = 'expired'
                    whatsapp_user.save()
                    
                    # Log event
                    WhatsAppSubscriptionEvent.objects.create(
                        whatsapp_user=whatsapp_user,
                        event_type='subscription_expired',
                        event_data={'expired_date': timezone.now().isoformat()}
                    )
                    
                    return 'expired'
            
        # Check trial status
        if whatsapp_user.trial_end_date and timezone.now() > whatsapp_user.trial_end_date:
            if whatsapp_user.subscription_status == 'premium' and not whatsapp_user.subscription:
                whatsapp_user.subscription_status = 'free'
                whatsapp_user.save()
                
                # Log event
                WhatsAppSubscriptionEvent.objects.create(
                    whatsapp_user=whatsapp_user,
                    event_type='trial_ended',
                    event_data={'ended_date': timezone.now().isoformat()}
                )
                
                return 'trial_ended'
        
        return whatsapp_user.subscription_status
```

### 3. Update WhatsApp Message Processor

#### Update whatsapp_integration/services.py
```python
from .subscription_service import WhatsAppSubscriptionService

class MessageProcessor:
    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.nlp_service = FootballNLPService()
        self.response_generator = ResponseGenerator()
        self.subscription_service = WhatsAppSubscriptionService()
    
    def process_incoming_message(self, message_data):
        # ... existing code ...
        
        # Check subscription status before processing
        subscription_status = self.subscription_service.check_subscription_status(user)
        
        # Handle subscription status changes
        if subscription_status in ['expired', 'trial_ended']:
            self.send_subscription_reminder(user, subscription_status)
        
        # Check rate limits with subscription awareness
        if not self.check_rate_limits(user):
            self.send_rate_limit_message(user.phone_number, user)
            return
        
        # Process message through NLP and generate response
        response = self.generate_response(message_text, user)
        self.whatsapp_service.send_text_message(user.phone_number, response)
    
    def check_rate_limits(self, user):
        # Update daily query count
        from datetime import date
        today = date.today()
        
        if user.last_query_date != today:
            user.daily_queries_count = 0
            user.last_query_date = today
            user.save()
        
        # Check limits based on subscription
        daily_limit = user.daily_limit
        if daily_limit and user.daily_queries_count >= daily_limit:
            return False
        
        user.daily_queries_count += 1
        user.save()
        return True
    
    def send_rate_limit_message(self, phone_number, user):
        if user.is_premium:
            message = "Você atingiu o limite mensal de consultas. Considere fazer upgrade para Pro."
        else:
            message = """📵 Limite diário atingido (5 consultas)

💎 Quer consultas ilimitadas?
Premium: R$ 19,90/mês
Pro: R$ 49,90/mês

🆓 Teste grátis 7 dias: Digite /trial
💳 Assinar agora: Digite /premium"""
        
        self.whatsapp_service.send_text_message(phone_number, message)
    
    def send_subscription_reminder(self, user, status):
        if status == 'expired':
            message = """⏰ Sua assinatura expirou

Renove agora e continue aproveitando:
✅ Consultas ilimitadas
✅ Análise completa de odds
✅ Previsões com IA

Digite /renovar para continuar"""
        else:  # trial_ended
            message = """🔚 Seu período de teste terminou

Gostou? Assine agora:
💎 Premium: R$ 19,90/mês
🏆 Pro: R$ 49,90/mês

Digite /premium para assinar"""
        
        self.whatsapp_service.send_text_message(user.phone_number, message)
    
    def generate_response(self, message_text, user):
        # Handle subscription commands
        message_lower = message_text.lower().strip()
        
        if message_lower.startswith('/premium'):
            return self.handle_premium_command(user)
        elif message_lower.startswith('/trial'):
            return self.handle_trial_command(user)
        elif message_lower.startswith('/cancelar'):
            return self.handle_cancel_command(user)
        elif message_lower.startswith('/renovar'):
            return self.handle_renew_command(user)
        elif message_lower.startswith('/status'):
            return self.handle_status_command(user)
        
        # Process with NLP for football queries
        query_result = self.nlp_service.process_query(message_text, user.phone_number)
        response = self.response_generator.generate_response(query_result, user)
        
        return response
    
    def handle_premium_command(self, user):
        if user.is_premium:
            return f"✅ Você já é usuário {user.subscription_status.title()}!"
        
        # Create payment links
        premium_result = self.subscription_service.create_subscription_payment_link(user, 'Premium')
        pro_result = self.subscription_service.create_subscription_payment_link(user, 'Pro')
        
        response = """💎 Mark Foot Premium

🥉 Premium (R$ 19,90/mês):
✅ Consultas ilimitadas
✅ Análise de odds
✅ Previsões IA

🥇 Pro (R$ 49,90/mês):
✅ Tudo do Premium +
✅ Relatórios PDF
✅ Suporte prioritário
✅ Grupos VIP

🔗 Escolha seu plano:"""
        
        if premium_result['success']:
            response += f"\n💎 Premium: {premium_result['payment_url']}"
        
        if pro_result['success']:
            response += f"\n🏆 Pro: {pro_result['payment_url']}"
        
        response += "\n\n🆓 Ou teste grátis 7 dias: Digite /trial"
        
        return response
    
    def handle_trial_command(self, user):
        if user.trial_used:
            return "❌ Você já utilizou seu período de teste gratuito."
        
        if user.is_premium:
            return "✅ Você já tem acesso premium!"
        
        result = self.subscription_service.start_free_trial(user)
        
        if result['success']:
            return f"""🎉 Trial Premium ativado!

✅ 7 dias de acesso completo
✅ Todas as funcionalidades Premium
⏰ Válido até {result['trial_end_date'].strftime('%d/%m/%Y')}

Aproveite! Digite qualquer pergunta sobre futebol."""
        else:
            return f"❌ Erro ao ativar trial: {result['message']}"
    
    def handle_cancel_command(self, user):
        if not user.subscription:
            return "❌ Você não possui assinatura ativa."
        
        result = self.subscription_service.cancel_subscription(user)
        
        if result['success']:
            return result['message']
        else:
            return f"❌ Erro ao cancelar: {result['message']}"
    
    def handle_renew_command(self, user):
        # Same as premium command for renewal
        return self.handle_premium_command(user)
    
    def handle_status_command(self, user):
        status = user.subscription_status
        
        if status == 'free':
            daily_used = user.daily_queries_count
            daily_limit = user.daily_limit or 5
            
            return f"""📊 Status da Conta

🆓 Plano: Gratuito
📱 Consultas hoje: {daily_used}/{daily_limit}
📅 Renovação: Diária

💎 Upgrade para Premium: /premium"""
        
        elif status in ['premium', 'pro']:
            subscription = user.subscription
            days_left = (subscription.end_date - timezone.now()).days if subscription else 0
            
            return f"""📊 Status da Conta

💎 Plano: {status.title()}
📅 Expira em: {days_left} dias
📱 Consultas: Ilimitadas
✅ Status: Ativo

❌ Cancelar: /cancelar"""
        
        elif status == 'expired':
            return """📊 Status da Conta

⏰ Status: Expirado
📱 Consultas: Limitado (5/dia)

🔄 Renovar: /renovar"""
        
        else:
            return "📊 Status: Verificando... Tente novamente em alguns segundos."
```

### 4. Webhook Handlers for Payment Providers

#### whatsapp_integration/webhooks.py
```python
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import hmac
import hashlib
from .services.subscription_service import WhatsAppSubscriptionService

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    subscription_service = WhatsAppSubscriptionService()
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        whatsapp_user_id = session['metadata'].get('whatsapp_user_id')
        
        if whatsapp_user_id:
            result = subscription_service.process_successful_payment(
                session['id'], 'stripe'
            )
            
            if result['success']:
                # Send confirmation via WhatsApp
                from .tasks import send_subscription_confirmation
                send_subscription_confirmation.delay(whatsapp_user_id)
    
    return HttpResponse(status=200)

@csrf_exempt
@require_http_methods(["POST"])
def pagseguro_webhook(request):
    # Implement PagSeguro webhook handling
    try:
        data = json.loads(request.body)
        # Process PagSeguro notification
        subscription_service = WhatsAppSubscriptionService()
        
        if data.get('event_type') == 'payment.approved':
            payment_id = data.get('data', {}).get('id')
            result = subscription_service.process_successful_payment(
                payment_id, 'pagseguro'
            )
            
            if result['success']:
                whatsapp_user_id = data.get('reference_id', '').split('_')[1]
                from .tasks import send_subscription_confirmation
                send_subscription_confirmation.delay(whatsapp_user_id)
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def mercadopago_webhook(request):
    # Implement Mercado Pago webhook handling
    try:
        data = json.loads(request.body)
        subscription_service = WhatsAppSubscriptionService()
        
        if data.get('type') == 'payment' and data.get('action') == 'payment.created':
            payment_id = data.get('data', {}).get('id')
            result = subscription_service.process_successful_payment(
                payment_id, 'mercadopago'
            )
            
            if result['success']:
                external_ref = data.get('external_reference', '')
                whatsapp_user_id = external_ref.split('_')[1]
                from .tasks import send_subscription_confirmation
                send_subscription_confirmation.delay(whatsapp_user_id)
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
```

### 5. Celery Tasks for Subscription Management

#### whatsapp_integration/tasks.py
```python
from celery import shared_task
from .models import WhatsAppUser, WhatsAppSubscriptionEvent
from .services import WhatsAppService

@shared_task
def send_subscription_confirmation(whatsapp_user_id):
    try:
        user = WhatsAppUser.objects.get(id=whatsapp_user_id)
        whatsapp_service = WhatsAppService()
        
        message = f"""🎉 Assinatura {user.current_plan.name} ativada!

✅ Acesso premium liberado
🔓 Consultas ilimitadas
💎 Análise completa de odds
🤖 Previsões com IA

Experimente agora: Digite qualquer pergunta sobre futebol!

📞 Dúvidas? Responda esta mensagem."""
        
        whatsapp_service.send_text_message(user.phone_number, message)
        
    except Exception as e:
        print(f"Error sending subscription confirmation: {e}")

@shared_task
def check_expiring_subscriptions():
    """Check for subscriptions expiring in 3 days"""
    from datetime import timedelta
    from django.utils import timezone
    
    expiring_date = timezone.now() + timedelta(days=3)
    
    expiring_users = WhatsAppUser.objects.filter(
        subscription__end_date__date=expiring_date.date(),
        subscription__status='active'
    )
    
    whatsapp_service = WhatsAppService()
    
    for user in expiring_users:
        message = """⏰ Sua assinatura expira em 3 dias

Renove agora e mantenha:
✅ Consultas ilimitadas
✅ Análise de odds
✅ Previsões IA

🔄 Renovar: /renovar
❓ Dúvidas: Responda esta mensagem"""
        
        whatsapp_service.send_text_message(user.phone_number, message)

@shared_task
def process_subscription_events():
    """Process pending subscription events"""
    events = WhatsAppSubscriptionEvent.objects.filter(processed=False)
    
    whatsapp_service = WhatsAppService()
    
    for event in events:
        try:
            if event.event_type == 'subscription_expired':
                message = """⏰ Sua assinatura expirou

Você voltou ao plano gratuito:
📱 5 consultas por dia
❌ Sem análise de odds

🔄 Renovar agora: /renovar"""
                
                whatsapp_service.send_text_message(
                    event.whatsapp_user.phone_number, 
                    message
                )
            
            elif event.event_type == 'trial_ended':
                message = """🔚 Período de teste finalizado

Gostou da experiência Premium?
💎 Continue com apenas R$ 19,90/mês

✅ Consultas ilimitadas
✅ Análise de odds
✅ Previsões IA

📝 Assinar: /premium"""
                
                whatsapp_service.send_text_message(
                    event.whatsapp_user.phone_number, 
                    message
                )
            
            event.processed = True
            event.save()
            
        except Exception as e:
            print(f"Error processing event {event.id}: {e}")
```

### 6. URL Configuration

#### Add to whatsapp_integration/urls.py
```python
from django.urls import path
from . import views, webhooks

urlpatterns = [
    path('webhook/', views.webhook, name='whatsapp_webhook'),
    path('webhooks/stripe/', webhooks.stripe_webhook, name='stripe_webhook'),
    path('webhooks/pagseguro/', webhooks.pagseguro_webhook, name='pagseguro_webhook'),
    path('webhooks/mercadopago/', webhooks.mercadopago_webhook, name='mercadopago_webhook'),
]
```

### 7. Admin Integration

#### Update whatsapp_integration/admin.py
```python
from django.contrib import admin
from .models import WhatsAppUser, WhatsAppPaymentIntent, WhatsAppSubscriptionEvent

@admin.register(WhatsAppUser)
class WhatsAppUserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'display_name', 'subscription_status', 'current_plan', 'created_at']
    list_filter = ['subscription_status', 'current_plan', 'trial_used']
    search_fields = ['phone_number', 'display_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(WhatsAppPaymentIntent)
class WhatsAppPaymentIntentAdmin(admin.ModelAdmin):
    list_display = ['whatsapp_user', 'plan', 'payment_provider', 'amount', 'status', 'created_at']
    list_filter = ['payment_provider', 'status']
    readonly_fields = ['created_at']

@admin.register(WhatsAppSubscriptionEvent)
class WhatsAppSubscriptionEventAdmin(admin.ModelAdmin):
    list_display = ['whatsapp_user', 'event_type', 'processed', 'created_at']
    list_filter = ['event_type', 'processed']
    readonly_fields = ['created_at']
```

## Integration Requirements

### Environment Variables
```
# Payment webhook secrets
STRIPE_WEBHOOK_SECRET=whsec_...
PAGSEGURO_WEBHOOK_SECRET=...
MERCADOPAGO_WEBHOOK_SECRET=...

# Frontend URL for redirects
FRONTEND_URL=https://markfoot.com
BACKEND_URL=https://api.markfoot.com
```

### Celery Beat Schedule
```python
CELERY_BEAT_SCHEDULE.update({
    'check-expiring-subscriptions': {
        'task': 'whatsapp_integration.tasks.check_expiring_subscriptions',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    'process-subscription-events': {
        'task': 'whatsapp_integration.tasks.process_subscription_events',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
})
```

## Expected Deliverables

1. WhatsApp subscription management system
2. Payment link generation for multiple providers
3. Webhook handlers for payment confirmations
4. Trial system with 7-day free access
5. Usage tracking and rate limiting
6. Subscription status checking and renewal reminders
7. Integration with existing billing system
8. Admin interface for subscription management

## Success Criteria

- Users can subscribe to premium plans via WhatsApp
- Payment confirmation triggers subscription activation
- Rate limiting works correctly for free/premium users
- Trial system provides temporary premium access
- Subscription expiration handling works properly
- Webhook integration processes payments successfully
- Admin can manage WhatsApp subscriptions
