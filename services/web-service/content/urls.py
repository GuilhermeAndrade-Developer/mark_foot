from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.ContentCategoryViewSet)
router.register(r'articles', views.UserArticleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('stats/', views.content_stats, name='content-stats'),
]
