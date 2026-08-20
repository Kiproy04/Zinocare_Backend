"""
URL configuration for Zinocare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView

api_v1_patterns = [
    path('accounts/', include('accounts.urls')),
    path('accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('livestock/', include('livestock.urls')),
    path('vaccinations/', include('vaccinations.urls')),
    path('consultations/', include('consultations.urls')),
    path('notifications/', include('notifications.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),

    # New versioned API
    path('api/v1/', include(api_v1_patterns)),

    # API Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]