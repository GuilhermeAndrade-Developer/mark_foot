from django.core.management.base import BaseCommand
from whatsapp_integration.models import WhatsAppUser
from whatsapp_integration.services.message_processor import MessageProcessor


class Command(BaseCommand):
    help = 'Test WhatsApp analytics commands'
    
    def add_arguments(self, parser):
        parser.add_argument('--phone', type=str, default='+5511999999999', help='Phone number')
        parser.add_argument('--message', type=str, required=True, help='Message to test')
    
    def handle(self, *args, **options):
        phone = options['phone']
        message = options['message']
        
        self.stdout.write(f"📱 Testing WhatsApp message: {message}")
        self.stdout.write(f"📞 Phone: {phone}")
        
        try:
            # Get or create WhatsApp user
            whatsapp_user, created = WhatsAppUser.objects.get_or_create(
                phone_number=phone,
                defaults={
                    'display_name': 'Test User',
                    'subscription_status': 'premium',  # Give premium for testing
                }
            )
            
            if created:
                self.stdout.write("👤 Created new WhatsApp user")
            else:
                self.stdout.write("👤 Using existing WhatsApp user")
            
            # Process message
            processor = MessageProcessor()
            processor._handle_user_message(whatsapp_user, message)
            
            self.stdout.write(self.style.SUCCESS("✅ Message processed successfully!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
