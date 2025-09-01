from django.urls import path
from . import views

app_name = 'nlp_engine'

urlpatterns = [
    path('process/', views.ProcessQueryView.as_view(), name='process_query'),
    path('intents/', views.IntentListView.as_view(), name='intent_list'),
    path('entities/', views.EntityTypeListView.as_view(), name='entity_list'),
    path('training/', views.TrainingPhraseListView.as_view(), name='training_list'),
    path('analytics/', views.QueryAnalyticsView.as_view(), name='analytics'),
]
