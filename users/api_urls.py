"""
API routes for users
"""

from django.urls import path
from . import api_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = 'users-api'

urlpatterns = [
    # CSRF token
    path('csrf/', api_views.CSRFTokenView.as_view(), name='api_csrf'),

    # Registration
    path('register/', api_views.RegisterAPIView.as_view(), name='api_register'),

    # JWT Token endpoints (NEW - use these!)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Old login (session-based) - keep for compatibility
    path('login/', api_views.LoginAPIView.as_view(), name='api_login'),

    # Logout
    path('logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),

    # Profile GET, UPDATE
    path('profile/', api_views.ProfileAPIView.as_view(), name='api_profile'),

    # Current user
    path('me/', api_views.MeAPIView.as_view(), name='api_me'),

    # Password change (authenticated users only)
    path('password-change/', api_views.PasswordChangeView.as_view(), name='password-change'),
]