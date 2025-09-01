from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import hmac
import hashlib
import logging
from .services.subscription_service import WhatsAppSubscriptionService
from .models import WhatsAppPaymentIntent

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        # Verify webhook signature (implement based on your Stripe settings)
        event_data = json.loads(payload)
        
        # Handle different event types
        event_type = event_data.get('type')
        
        if event_type == 'payment_intent.succeeded':
            payment_intent = event_data['data']['object']
            metadata = payment_intent.get('metadata', {})
            
            if 'payment_intent_id' in metadata:
                subscription_service = WhatsAppSubscriptionService()
                result = subscription_service.process_successful_payment(
                    payment_intent_id=metadata['payment_intent_id'],
                    provider_transaction_id=payment_intent['id']
                )
                
                if result['success']:
                    logger.info(f"Stripe payment processed successfully: {payment_intent['id']}")
                else:
                    logger.error(f"Error processing Stripe payment: {result['message']}")
        
        elif event_type == 'payment_intent.payment_failed':
            payment_intent = event_data['data']['object']
            metadata = payment_intent.get('metadata', {})
            
            if 'payment_intent_id' in metadata:
                try:
                    payment_record = WhatsAppPaymentIntent.objects.get(
                        id=metadata['payment_intent_id']
                    )
                    payment_record.status = 'failed'
                    payment_record.save()
                    logger.info(f"Stripe payment failed: {payment_intent['id']}")
                except WhatsAppPaymentIntent.DoesNotExist:
                    logger.error(f"Payment intent not found: {metadata['payment_intent_id']}")
        
        return HttpResponse(status=200)
        
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        return HttpResponse(status=400)


@csrf_exempt
@require_http_methods(["POST"])
def pagseguro_webhook(request):
    """Handle PagSeguro webhook events"""
    try:
        data = json.loads(request.body)
        
        # PagSeguro sends different event structures
        notification_code = data.get('notificationCode')
        notification_type = data.get('notificationType')
        
        if notification_type == 'transaction':
            # Process transaction notification
            # You would typically fetch transaction details from PagSeguro API here
            reference_id = data.get('reference')
            
            if reference_id:
                subscription_service = WhatsAppSubscriptionService()
                result = subscription_service.process_successful_payment(
                    payment_intent_id=reference_id,
                    provider_transaction_id=notification_code
                )
                
                if result['success']:
                    logger.info(f"PagSeguro payment processed successfully: {notification_code}")
                else:
                    logger.error(f"Error processing PagSeguro payment: {result['message']}")
        
        return HttpResponse(status=200)
        
    except Exception as e:
        logger.error(f"Error processing PagSeguro webhook: {str(e)}")
        return HttpResponse(status=400)


@csrf_exempt
@require_http_methods(["POST"])
def mercadopago_webhook(request):
    """Handle Mercado Pago webhook events"""
    try:
        data = json.loads(request.body)
        
        # Mercado Pago webhook structure
        resource = data.get('resource')
        topic = data.get('topic')
        
        if topic == 'payment':
            # Extract payment ID from resource URL
            payment_id = resource.split('/')[-1] if resource else None
            
            if payment_id:
                # Find payment intent by Mercado Pago payment ID
                try:
                    payment_intent = WhatsAppPaymentIntent.objects.get(
                        mercadopago_payment_id=payment_id
                    )
                    
                    subscription_service = WhatsAppSubscriptionService()
                    result = subscription_service.process_successful_payment(
                        payment_intent_id=payment_intent.id,
                        provider_transaction_id=payment_id
                    )
                    
                    if result['success']:
                        logger.info(f"Mercado Pago payment processed successfully: {payment_id}")
                    else:
                        logger.error(f"Error processing Mercado Pago payment: {result['message']}")
                        
                except WhatsAppPaymentIntent.DoesNotExist:
                    logger.error(f"Payment intent not found for Mercado Pago payment: {payment_id}")
        
        return HttpResponse(status=200)
        
    except Exception as e:
        logger.error(f"Error processing Mercado Pago webhook: {str(e)}")
        return HttpResponse(status=400)


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(View):
    """Enhanced WhatsApp webhook view with subscription handling"""
    
    def get(self, request):
        """Verify webhook URL (WhatsApp requirement)"""
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        if mode == 'subscribe' and token == getattr(settings, 'WHATSAPP_VERIFY_TOKEN', ''):
            return HttpResponse(challenge)
        
        return HttpResponse(status=403)
    
    def post(self, request):
        """Handle incoming WhatsApp messages"""
        try:
            data = json.loads(request.body)
            
            # Import here to avoid circular imports
            from .services import MessageProcessor
            
            processor = MessageProcessor()
            processor.process_message(data)
            
            return HttpResponse(status=200)
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp webhook: {str(e)}")
            return HttpResponse(status=500)
