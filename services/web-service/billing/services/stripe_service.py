"""
Stripe payment service integration
"""

import stripe
import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from typing import Dict, Any, Optional
from ..models import UserSubscription, SubscriptionPlan, PaymentMethod, Invoice

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for handling Stripe payments and subscriptions"""
    
    def __init__(self):
        self.stripe = stripe
        
    def create_payment_intent(self, amount: int, currency: str = 'brl', metadata: dict = None) -> Dict[str, Any]:
        """Create a Stripe PaymentIntent for one-time payments"""
        try:
            payment_intent = self.stripe.PaymentIntent.create(
                amount=amount,  # Amount in cents
                currency=currency,
                metadata=metadata or {},
                payment_method_types=['card'],
            )
            
            logger.info(f"Created Stripe PaymentIntent {payment_intent.id}")
            return {
                'success': True,
                'id': payment_intent.id,
                'client_secret': payment_intent.client_secret,
                'payment_intent': payment_intent
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create PaymentIntent: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_customer(self, user: User) -> Dict[str, Any]:
        """Create a Stripe customer for the user"""
        try:
            customer = self.stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}".strip() or user.username,
                metadata={
                    'user_id': user.id,
                    'username': user.username
                }
            )
            logger.info(f"Created Stripe customer {customer.id} for user {user.id}")
            return {
                'success': True,
                'customer_id': customer.id,
                'customer': customer
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer for user {user.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_payment_method(self, user: User, payment_method_id: str) -> Dict[str, Any]:
        """Attach payment method to customer"""
        try:
            # First, ensure user has a Stripe customer
            customer_result = self.get_or_create_customer(user)
            if not customer_result['success']:
                return customer_result
            
            customer_id = customer_result['customer_id']
            
            # Attach payment method to customer
            payment_method = self.stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            
            # Get payment method details
            pm_details = self.stripe.PaymentMethod.retrieve(payment_method_id)
            
            # Save payment method in our database
            if pm_details.type == 'card':
                card = pm_details.card
                payment_method_obj = PaymentMethod.objects.create(
                    user=user,
                    payment_type='credit_card',
                    card_last_four=card.last4,
                    card_brand=card.brand,
                    card_exp_month=card.exp_month,
                    card_exp_year=card.exp_year,
                    stripe_payment_method_id=payment_method_id
                )
                
                # Set as default if it's the user's first payment method
                if not PaymentMethod.objects.filter(user=user, is_default=True).exists():
                    payment_method_obj.is_default = True
                    payment_method_obj.save()
            
            logger.info(f"Attached payment method {payment_method_id} to customer {customer_id}")
            return {
                'success': True,
                'payment_method': payment_method,
                'payment_method_obj': payment_method_obj
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to attach payment method for user {user.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_subscription(self, user: User, plan: SubscriptionPlan, payment_method_id: str = None) -> Dict[str, Any]:
        """Create a Stripe subscription"""
        try:
            # Get or create customer
            customer_result = self.get_or_create_customer(user)
            if not customer_result['success']:
                return customer_result
            
            customer_id = customer_result['customer_id']
            
            # Create Stripe product if not exists
            product_result = self.get_or_create_product(plan)
            if not product_result['success']:
                return product_result
            
            # Create Stripe price
            price_result = self.get_or_create_price(plan, product_result['product_id'])
            if not price_result['success']:
                return price_result
            
            # Set default payment method if provided
            if payment_method_id:
                self.stripe.Customer.modify(
                    customer_id,
                    invoice_settings={'default_payment_method': payment_method_id}
                )
            
            # Create subscription
            subscription = self.stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_result['price_id']}],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
                metadata={
                    'user_id': user.id,
                    'plan_id': plan.id
                }
            )
            
            logger.info(f"Created Stripe subscription {subscription.id} for user {user.id}")
            return {
                'success': True,
                'subscription': subscription,
                'subscription_id': subscription.id,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create subscription for user {user.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Cancel a Stripe subscription"""
        try:
            subscription = self.stripe.Subscription.cancel(subscription_id)
            logger.info(f"Cancelled Stripe subscription {subscription_id}")
            return {
                'success': True,
                'subscription': subscription
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription {subscription_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_subscription(self, subscription_id: str, new_plan: SubscriptionPlan) -> Dict[str, Any]:
        """Update subscription to new plan"""
        try:
            # Get current subscription
            subscription = self.stripe.Subscription.retrieve(subscription_id)
            
            # Create new price for the plan
            product_result = self.get_or_create_product(new_plan)
            if not product_result['success']:
                return product_result
            
            price_result = self.get_or_create_price(new_plan, product_result['product_id'])
            if not price_result['success']:
                return price_result
            
            # Update subscription
            updated_subscription = self.stripe.Subscription.modify(
                subscription_id,
                items=[{
                    'id': subscription['items']['data'][0].id,
                    'price': price_result['price_id'],
                }],
                proration_behavior='immediate_with_payment',
            )
            
            logger.info(f"Updated Stripe subscription {subscription_id} to plan {new_plan.id}")
            return {
                'success': True,
                'subscription': updated_subscription
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Failed to update subscription {subscription_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_or_create_customer(self, user: User) -> Dict[str, Any]:
        """Get existing customer or create new one"""
        try:
            # Try to find existing customer by email
            customers = self.stripe.Customer.list(email=user.email, limit=1)
            
            if customers.data:
                customer = customers.data[0]
                return {
                    'success': True,
                    'customer_id': customer.id,
                    'customer': customer
                }
            else:
                # Create new customer
                return self.create_customer(user)
                
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get/create customer for user {user.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_or_create_product(self, plan: SubscriptionPlan) -> Dict[str, Any]:
        """Get or create Stripe product for plan"""
        try:
            # Try to find existing product
            products = self.stripe.Product.list(
                metadata={'plan_id': str(plan.id)},
                limit=1
            )
            
            if products.data:
                product = products.data[0]
                return {
                    'success': True,
                    'product_id': product.id,
                    'product': product
                }
            else:
                # Create new product
                product = self.stripe.Product.create(
                    name=plan.name,
                    description=plan.description,
                    metadata={
                        'plan_id': plan.id,
                        'plan_type': plan.plan_type
                    }
                )
                
                logger.info(f"Created Stripe product {product.id} for plan {plan.id}")
                return {
                    'success': True,
                    'product_id': product.id,
                    'product': product
                }
                
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get/create product for plan {plan.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_or_create_price(self, plan: SubscriptionPlan, product_id: str) -> Dict[str, Any]:
        """Get or create Stripe price for plan"""
        try:
            # Try to find existing price
            prices = self.stripe.Price.list(
                product=product_id,
                metadata={'plan_id': str(plan.id)},
                limit=1
            )
            
            if prices.data:
                price = prices.data[0]
                return {
                    'success': True,
                    'price_id': price.id,
                    'price': price
                }
            else:
                # Create new price
                price = self.stripe.Price.create(
                    product=product_id,
                    unit_amount=int(plan.price_monthly * 100),  # Convert to cents
                    currency='brl',
                    recurring={'interval': 'month'},
                    metadata={
                        'plan_id': plan.id,
                        'plan_type': plan.plan_type
                    }
                )
                
                logger.info(f"Created Stripe price {price.id} for plan {plan.id}")
                return {
                    'success': True,
                    'price_id': price.id,
                    'price': price
                }
                
        except stripe.error.StripeError as e:
            logger.error(f"Failed to get/create price for plan {plan.id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_webhook(self, payload: str, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            
            logger.info(f"Received Stripe webhook: {event['type']}")
            
            if event['type'] == 'invoice.payment_succeeded':
                return self._handle_payment_succeeded(event['data']['object'])
            elif event['type'] == 'invoice.payment_failed':
                return self._handle_payment_failed(event['data']['object'])
            elif event['type'] == 'customer.subscription.updated':
                return self._handle_subscription_updated(event['data']['object'])
            elif event['type'] == 'customer.subscription.deleted':
                return self._handle_subscription_deleted(event['data']['object'])
            
            return {'success': True, 'message': f"Unhandled event type: {event['type']}"}
            
        except ValueError as e:
            logger.error(f"Invalid Stripe webhook payload: {e}")
            return {'success': False, 'error': 'Invalid payload'}
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid Stripe webhook signature: {e}")
            return {'success': False, 'error': 'Invalid signature'}
    
    def _handle_payment_succeeded(self, invoice_data: Dict) -> Dict[str, Any]:
        """Handle successful payment"""
        try:
            subscription_id = invoice_data.get('subscription')
            if not subscription_id:
                return {'success': True, 'message': 'No subscription in invoice'}
            
            # Find our subscription
            try:
                user_subscription = UserSubscription.objects.get(
                    stripe_subscription_id=subscription_id
                )
                
                # Update subscription status
                user_subscription.status = 'active'
                user_subscription.save()
                
                # Create invoice record
                Invoice.objects.create(
                    user=user_subscription.user,
                    subscription=user_subscription,
                    subtotal=Decimal(invoice_data['amount_paid']) / 100,
                    total_amount=Decimal(invoice_data['amount_paid']) / 100,
                    status='paid',
                    stripe_invoice_id=invoice_data['id'],
                    billing_period_start=user_subscription.started_at,
                    billing_period_end=user_subscription.expires_at,
                    due_date=user_subscription.expires_at
                )
                
                logger.info(f"Payment succeeded for subscription {subscription_id}")
                return {'success': True, 'message': 'Payment processed'}
                
            except UserSubscription.DoesNotExist:
                logger.warning(f"Subscription {subscription_id} not found in database")
                return {'success': True, 'message': 'Subscription not found'}
                
        except Exception as e:
            logger.error(f"Error handling payment success: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_payment_failed(self, invoice_data: Dict) -> Dict[str, Any]:
        """Handle failed payment"""
        try:
            subscription_id = invoice_data.get('subscription')
            if not subscription_id:
                return {'success': True, 'message': 'No subscription in invoice'}
            
            # Find our subscription
            try:
                user_subscription = UserSubscription.objects.get(
                    stripe_subscription_id=subscription_id
                )
                
                # Update subscription status
                user_subscription.status = 'pending'
                user_subscription.save()
                
                logger.info(f"Payment failed for subscription {subscription_id}")
                return {'success': True, 'message': 'Payment failure processed'}
                
            except UserSubscription.DoesNotExist:
                logger.warning(f"Subscription {subscription_id} not found in database")
                return {'success': True, 'message': 'Subscription not found'}
                
        except Exception as e:
            logger.error(f"Error handling payment failure: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_subscription_updated(self, subscription_data: Dict) -> Dict[str, Any]:
        """Handle subscription updates"""
        # Implementation for subscription updates
        return {'success': True, 'message': 'Subscription update processed'}
    
    def _handle_subscription_deleted(self, subscription_data: Dict) -> Dict[str, Any]:
        """Handle subscription cancellation"""
        try:
            subscription_id = subscription_data['id']
            
            # Find our subscription
            try:
                user_subscription = UserSubscription.objects.get(
                    stripe_subscription_id=subscription_id
                )
                
                # Update subscription status
                user_subscription.status = 'cancelled'
                user_subscription.cancelled_at = timezone.now()
                user_subscription.save()
                
                logger.info(f"Subscription {subscription_id} cancelled")
                return {'success': True, 'message': 'Subscription cancellation processed'}
                
            except UserSubscription.DoesNotExist:
                logger.warning(f"Subscription {subscription_id} not found in database")
                return {'success': True, 'message': 'Subscription not found'}
                
        except Exception as e:
            logger.error(f"Error handling subscription deletion: {e}")
            return {'success': False, 'error': str(e)}
