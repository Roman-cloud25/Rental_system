"""
API routes for users
"""

from django.urls import path
from . import api_views

app_name = 'users-api'

urlpatterns = [
    # CSRF token
    path('csrf/',    api_views.CSRFTokenView.as_view(), name='api_csrf'),

    # Registration
    path('register/', api_views.RegisterAPIView.as_view(), name='api_register'),

    # Login
    path('login/', api_views.LoginAPIView.as_view(), name='api_login'),

    # Logout
    path('logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),

    # Profile GET, UPDATE
    path('profile/', api_views.ProfileAPIView.as_view(), name='api_profile'),

    # Current user
    path('me/', api_views.MeAPIView.as_view(), name='api_me'),
]
