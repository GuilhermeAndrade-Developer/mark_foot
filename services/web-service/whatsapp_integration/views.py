from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import hashlib
import hmac
import logging
from .models import WhatsAppUser, WhatsAppMessage, WhatsAppSession
from .services import WhatsAppService, MessageProcessor
from .tasks import process_whatsapp_message

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def webhook(request):
    """WhatsApp webhook endpoint"""
    if request.method == "GET":
        # Webhook verification
        return verify_webhook(request)
    
    elif request.method == "POST":
        # Process incoming message
        return process_webhook(request)

def verify_webhook(request):
    """Verify webhook during setup"""
    verify_token = request.GET.get('hub.verify_token')
    challenge = request.GET.get('hub.challenge')
    
    if verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp webhook verified successfully")
        return HttpResponse(challenge)
    else:
        logger.warning("Invalid WhatsApp webhook verification token")
        return HttpResponse("Invalid verification token", status=403)

def process_webhook(request):
    """Process incoming WhatsApp webhook"""
    try:
        # Verify webhook signature
        if not verify_webhook_signature(request):
            logger.warning("Invalid webhook signature")
            return HttpResponse("Invalid signature", status=403)
        
        # Parse webhook data
        webhook_data = json.loads(request.body)
        
        # Process message asynchronously
        process_whatsapp_message.delay(webhook_data)
        
        return JsonResponse({"status": "success"})
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}")
        return JsonResponse({"error": "Processing failed"}, status=500)

def verify_webhook_signature(request):
    """Verify webhook signature from Meta"""
    signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
    if not signature:
        return False
    
    try:
        expected_signature = hmac.new(
            settings.WHATSAPP_APP_SECRET.encode('utf-8'),
            request.body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature[7:], expected_signature)
    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False

@csrf_exempt
def test_webhook(request):
    """Test endpoint for development"""
    if not settings.DEBUG:
        return JsonResponse({"error": "Not available in production"}, status=404)
    
    if request.method == "POST":
        try:
            webhook_data = json.loads(request.body)
            logger.info(f"Test webhook received: {webhook_data}")
            
            # Process message for testing
            process_whatsapp_message.delay(webhook_data)
            
            return JsonResponse({"status": "test_success", "data": webhook_data})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)
