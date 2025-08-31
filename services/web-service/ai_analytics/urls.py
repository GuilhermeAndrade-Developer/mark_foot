from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.ai_stats, name='ai_stats'),
    path('sentiment/', views.sentiment_analysis_list, name='sentiment_list'),
    path('test/', views.test_ai_services, name='test_ai'),
]
