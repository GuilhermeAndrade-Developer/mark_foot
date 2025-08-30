"""
URL configuration for test environment
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/test/', include('test_apps.api.urls')),
]
