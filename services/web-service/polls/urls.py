from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'polls', views.PollViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', views.polls_stats, name='polls-stats'),
]
