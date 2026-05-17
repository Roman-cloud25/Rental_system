"""
URL configuration for rental project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


# Swagger settings
schema_view = get_schema_view(
    openapi.Info(
        title="Rental System API",
        default_version='v1',
        description="API for the housing rental system\n\n"
                    "## Functionality:\n"
                    "- User management (registration, login)\n"
                    "- Listing management (CRUD)\n"
                    "- Search and filtering\n"
                    "- Housing booking\n"
                    "- Reviews and ratings\n"
                    "- Search and view history",
        contact=openapi.Contact(email="support@rental.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Django Admin panel
    path('admin/', admin.site.urls),

    # Documentation API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger/json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),

    # API routes
    # Registration, login, profile
    path('api/auth/', include('users.api_urls')),
    # Announcements
    path('api/properties/', include('properties.api_urls')),
    # Booking
    path('api/bookings/', include('bookings.api_urls')),
    # Reviews
    path('api/reviews/', include('reviews.api_urls')),
    # Analytics
    path('api/analytics/', include('analytics.api_urls')),

]

# Images
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)