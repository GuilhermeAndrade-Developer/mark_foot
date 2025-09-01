from django.core.management.base import BaseCommand
from django.conf import settings
import stripe


class Command(BaseCommand):
    help = 'Test payment gateway configurations'

    def handle(self, *args, **options):
        self.stdout.write("=== PAYMENT GATEWAY CONFIGURATION TEST ===\n")
        
        # Test Stripe
        self.stdout.write("🔵 Testing Stripe Configuration:")
        try:
            stripe_pk = getattr(settings, 'STRIPE_PUBLISHABLE_KEY', None)
            stripe_sk = getattr(settings, 'STRIPE_SECRET_KEY', None)
            
            self.stdout.write(f"Publishable Key: {stripe_pk[:20]}..." if stripe_pk else "❌ No publishable key")
            self.stdout.write(f"Secret Key: {stripe_sk[:20]}..." if stripe_sk else "❌ No secret key")
            
            if stripe_sk:
                stripe.api_key = stripe_sk
                # Test API connection
                try:
                    account = stripe.Account.retrieve()
                    self.stdout.write(self.style.SUCCESS(f"✅ Stripe connection successful"))
                    self.stdout.write(f"Account ID: {account.id}")
                    self.stdout.write(f"Country: {account.country}")
                except stripe.error.StripeError as e:
                    self.stdout.write(self.style.WARNING(f"⚠️ Stripe API test failed: {e}"))
            else:
                self.stdout.write(self.style.ERROR("❌ No Stripe secret key configured"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Stripe test error: {e}"))
        
        self.stdout.write("\n" + "="*50)
        
        # Test PagSeguro
        self.stdout.write("\n🟠 Testing PagSeguro Configuration:")
        try:
            pagseguro_email = getattr(settings, 'PAGSEGURO_EMAIL', None)
            pagseguro_token = getattr(settings, 'PAGSEGURO_TOKEN', None)
            pagseguro_sandbox = getattr(settings, 'PAGSEGURO_SANDBOX', True)
            
            self.stdout.write(f"Email: {pagseguro_email}" if pagseguro_email else "❌ No email")
            self.stdout.write(f"Token: {pagseguro_token[:20]}..." if pagseguro_token else "❌ No token")
            self.stdout.write(f"Sandbox: {pagseguro_sandbox}")
            
            if pagseguro_email and pagseguro_token:
                self.stdout.write(self.style.SUCCESS("✅ PagSeguro configured"))
            else:
                self.stdout.write(self.style.ERROR("❌ PagSeguro not fully configured"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ PagSeguro test error: {e}"))
        
        self.stdout.write("\n" + "="*50)
        
        # Test Mercado Pago
        self.stdout.write("\n🟡 Testing Mercado Pago Configuration:")
        try:
            mp_token = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', None)
            mp_sandbox = getattr(settings, 'MERCADOPAGO_SANDBOX', True)
            
            self.stdout.write(f"Access Token: {mp_token[:20]}..." if mp_token else "❌ No access token")
            self.stdout.write(f"Sandbox: {mp_sandbox}")
            
            if mp_token:
                self.stdout.write(self.style.SUCCESS("✅ Mercado Pago configured"))
                # Could test API here too
            else:
                self.stdout.write(self.style.ERROR("❌ Mercado Pago not configured"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Mercado Pago test error: {e}"))
        
        self.stdout.write("\n" + "="*50 + "\n")
