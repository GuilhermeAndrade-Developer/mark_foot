from django.urls import path
from . import views, webhooks

urlpatterns = [
    path('webhook/', views.webhook, name='whatsapp_webhook'),
    path('test-webhook/', views.test_webhook, name='whatsapp_test_webhook'),
    path('webhooks/stripe/', webhooks.stripe_webhook, name='stripe_webhook'),
    path('webhooks/pagseguro/', webhooks.pagseguro_webhook, name='pagseguro_webhook'),
    path('webhooks/mercadopago/', webhooks.mercadopago_webhook, name='mercadopago_webhook'),
]
