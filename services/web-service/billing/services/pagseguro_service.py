"""
PagSeguro payment service integration for Brazilian payments
"""

import requests
import logging
import xml.etree.ElementTree as ET
from django.conf import settings
from django.contrib.auth.models import User
from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from django.utils import timezone
from ..models import UserSubscription, SubscriptionPlan, PaymentMethod, Invoice

logger = logging.getLogger(__name__)


class PagSeguroService:
    """Service for handling PagSeguro payments (PIX, Boleto, Credit Card)"""
    
    def __init__(self):
        self.email = settings.PAGSEGURO_EMAIL
        self.token = settings.PAGSEGURO_TOKEN
        self.sandbox = settings.PAGSEGURO_SANDBOX
        
        if self.sandbox:
            self.base_url = 'https://ws.sandbox.pagseguro.uol.com.br'
            self.checkout_url = 'https://sandbox.pagseguro.uol.com.br'
        else:
            self.base_url = 'https://ws.pagseguro.uol.com.br'
            self.checkout_url = 'https://pagseguro.uol.com.br'
    
    def create_payment_request(self, user: User, plan: SubscriptionPlan, payment_method: str = 'all') -> Dict[str, Any]:
        """Create a PagSeguro payment request"""
        try:
            # Prepare payment data
            payment_data = {
                'email': self.email,
                'token': self.token,
                'currency': 'BRL',
                'itemId1': f'plan_{plan.id}',
                'itemDescription1': plan.name,
                'itemAmount1': f'{plan.price_monthly:.2f}',
                'itemQuantity1': '1',
                'senderName': f"{user.first_name} {user.last_name}".strip() or user.username,
                'senderEmail': user.email,
                'reference': f'user_{user.id}_plan_{plan.id}',
                'redirectURL': f'{settings.FRONTEND_URL}/pagamento/sucesso',
                'notificationURL': f'{settings.BACKEND_URL}/api/billing/webhooks/pagseguro/',
            }
            
            # Add payment method restrictions if specified
            if payment_method == 'pix':
                payment_data['paymentMethodGroup1'] = 'INSTANT_TRANSFER'
            elif payment_method == 'boleto':
                payment_data['paymentMethodGroup1'] = 'BOLETO'
            elif payment_method == 'credit_card':
                payment_data['paymentMethodGroup1'] = 'CREDIT_CARD'
            
            # Make request to PagSeguro
            response = requests.post(
                f'{self.base_url}/v2/checkout',
                data=payment_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                # Parse XML response
                root = ET.fromstring(response.content)
                checkout_code = root.find('code').text
                
                # Generate payment URL
                payment_url = f'{self.checkout_url}/v2/checkout/payment.html?code={checkout_code}'
                
                logger.info(f"Created PagSeguro payment request for user {user.id}, plan {plan.id}")
                return {
                    'success': True,
                    'checkout_code': checkout_code,
                    'payment_url': payment_url
                }
            else:
                logger.error(f"PagSeguro API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'PagSeguro API error: {response.status_code}'
                }
                
        except requests.RequestException as e:
            logger.error(f"Network error creating PagSeguro payment: {e}")
            return {
                'success': False,
                'error': 'Network error'
            }
        except ET.ParseError as e:
            logger.error(f"XML parse error from PagSeguro: {e}")
            return {
                'success': False,
                'error': 'Invalid response format'
            }
        except Exception as e:
            logger.error(f"Unexpected error creating PagSeguro payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_subscription_plan_pagseguro(self, plan: SubscriptionPlan) -> Dict[str, Any]:
        """Create a recurring payment plan in PagSeguro"""
        try:
            # PagSeguro preapproval data
            preapproval_data = {
                'email': self.email,
                'token': self.token,
                'preApprovalCharge': 'auto',
                'preApprovalName': plan.name,
                'preApprovalDetails': plan.description,
                'preApprovalAmountPerPayment': f'{plan.price_monthly:.2f}',
                'preApprovalPeriod': 'monthly',
                'preApprovalMaxAmountPerPeriod': f'{plan.price_monthly:.2f}',
                'reviewURL': f'{settings.FRONTEND_URL}/assinatura/revisao',
                'preApprovalMaxTotalAmount': f'{plan.price_monthly * 12:.2f}',  # 1 year max
                'reference': f'subscription_plan_{plan.id}',
            }
            
            response = requests.post(
                f'{self.base_url}/v2/pre-approvals/request',
                data=preapproval_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                preapproval_code = root.find('code').text
                
                logger.info(f"Created PagSeguro subscription plan for {plan.id}")
                return {
                    'success': True,
                    'preapproval_code': preapproval_code,
                    'subscription_url': f'{self.checkout_url}/v2/pre-approvals/request.html?code={preapproval_code}'
                }
            else:
                logger.error(f"PagSeguro subscription API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f'PagSeguro API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error creating PagSeguro subscription plan: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check transaction status in PagSeguro"""
        try:
            response = requests.get(
                f'{self.base_url}/v3/transactions/{transaction_id}',
                params={'email': self.email, 'token': self.token},
                timeout=30
            )
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                status_code = root.find('status').text
                status_mapping = {
                    '1': 'pending',      # Aguardando pagamento
                    '2': 'pending',      # Em análise
                    '3': 'paid',         # Paga
                    '4': 'paid',         # Disponível
                    '5': 'cancelled',    # Em disputa
                    '6': 'refunded',     # Devolvida
                    '7': 'cancelled',    # Cancelada
                }
                
                status = status_mapping.get(status_code, 'unknown')
                amount = float(root.find('grossAmount').text)
                
                return {
                    'success': True,
                    'status': status,
                    'amount': amount,
                    'transaction_data': root
                }
            else:
                logger.error(f"Error checking PagSeguro transaction {transaction_id}: {response.status_code}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error checking PagSeguro transaction {transaction_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_webhook(self, notification_code: str, notification_type: str) -> Dict[str, Any]:
        """Handle PagSeguro webhook notification"""
        try:
            if notification_type == 'transaction':
                return self._handle_transaction_notification(notification_code)
            elif notification_type == 'preApproval':
                return self._handle_subscription_notification(notification_code)
            else:
                return {
                    'success': True,
                    'message': f'Unhandled notification type: {notification_type}'
                }
                
        except Exception as e:
            logger.error(f"Error handling PagSeguro webhook: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_transaction_notification(self, notification_code: str) -> Dict[str, Any]:
        """Handle transaction notification from PagSeguro"""
        try:
            # Get transaction details
            response = requests.get(
                f'{self.base_url}/v3/transactions/notifications/{notification_code}',
                params={'email': self.email, 'token': self.token},
                timeout=30
            )
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                reference = root.find('reference').text
                status_code = root.find('status').text
                amount = float(root.find('grossAmount').text)
                transaction_id = root.find('code').text
                
                # Parse reference to get user and plan
                if reference and reference.startswith('user_'):
                    parts = reference.split('_')
                    if len(parts) >= 4:  # user_X_plan_Y
                        user_id = int(parts[1])
                        plan_id = int(parts[3])
                        
                        try:
                            user = User.objects.get(id=user_id)
                            plan = SubscriptionPlan.objects.get(id=plan_id)
                            
                            # Handle payment based on status
                            status_mapping = {
                                '1': 'pending',
                                '2': 'pending',
                                '3': 'paid',
                                '4': 'paid',
                                '5': 'cancelled',
                                '6': 'refunded',
                                '7': 'cancelled',
                            }
                            
                            status = status_mapping.get(status_code, 'unknown')
                            
                            if status == 'paid':
                                # Create or update subscription
                                subscription, created = UserSubscription.objects.get_or_create(
                                    user=user,
                                    defaults={
                                        'plan': plan,
                                        'status': 'active',
                                        'expires_at': timezone.now() + timedelta(days=30),
                                        'api_calls_reset_date': timezone.now() + timedelta(days=30),
                                        'pagseguro_subscription_id': transaction_id
                                    }
                                )
                                
                                if not created:
                                    subscription.status = 'active'
                                    subscription.expires_at = timezone.now() + timedelta(days=30)
                                    subscription.save()
                                
                                # Create invoice
                                Invoice.objects.create(
                                    user=user,
                                    subscription=subscription,
                                    subtotal=Decimal(amount),
                                    total_amount=Decimal(amount),
                                    status='paid',
                                    pagseguro_invoice_id=transaction_id,
                                    billing_period_start=timezone.now(),
                                    billing_period_end=subscription.expires_at,
                                    due_date=subscription.expires_at,
                                    paid_at=timezone.now()
                                )
                                
                                logger.info(f"PagSeguro payment confirmed for user {user_id}, plan {plan_id}")
                            
                            return {
                                'success': True,
                                'message': f'Transaction {transaction_id} status: {status}'
                            }
                            
                        except (User.DoesNotExist, SubscriptionPlan.DoesNotExist) as e:
                            logger.error(f"User or plan not found for reference {reference}: {e}")
                            return {
                                'success': False,
                                'error': 'User or plan not found'
                            }
                
                return {
                    'success': True,
                    'message': f'Transaction processed: {transaction_id}'
                }
            else:
                logger.error(f"Error getting PagSeguro notification details: {response.status_code}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error handling PagSeguro transaction notification: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _handle_subscription_notification(self, notification_code: str) -> Dict[str, Any]:
        """Handle subscription notification from PagSeguro"""
        # Implementation for subscription notifications
        return {
            'success': True,
            'message': 'Subscription notification processed'
        }
    
    def cancel_subscription(self, preapproval_code: str) -> Dict[str, Any]:
        """Cancel a PagSeguro subscription"""
        try:
            response = requests.put(
                f'{self.base_url}/v2/pre-approvals/{preapproval_code}/cancel',
                data={
                    'email': self.email,
                    'token': self.token
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=30
            )
            
            if response.status_code == 204:  # No content = success
                logger.info(f"Cancelled PagSeguro subscription {preapproval_code}")
                return {
                    'success': True,
                    'message': 'Subscription cancelled'
                }
            else:
                logger.error(f"Error cancelling PagSeguro subscription: {response.status_code}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error cancelling PagSeguro subscription {preapproval_code}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test PagSeguro API connection"""
        try:
            response = requests.get(
                f'{self.base_url}/v2/sessions',
                params={'email': self.email, 'token': self.token},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'PagSeguro connection successful'
                }
            else:
                return {
                    'success': False,
                    'error': f'API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"PagSeguro connection test failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
