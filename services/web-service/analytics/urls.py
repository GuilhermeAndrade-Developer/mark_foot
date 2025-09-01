from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'reports', views.AnalyticsReportViewSet, basename='analyticsreport')
router.register(r'dashboards', views.AnalyticsDashboardViewSet, basename='analyticsdashboard')
router.register(r'preferences', views.UserAnalyticsPreferenceViewSet, basename='useranalyticspreference')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Additional endpoints
    path('stats/', views.analytics_stats, name='analytics-stats'),
    path('teams-players/', views.available_teams_and_players, name='available-teams-players'),
]
