from django.urls import path
from . import views

urlpatterns = [
    path('webhook/', views.webhook, name='whatsapp_webhook'),
    path('test-webhook/', views.test_webhook, name='whatsapp_test_webhook'),
]
