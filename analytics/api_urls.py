"""
API routes for analytics
"""

from django.urls import path
from . import api_views

app_name = 'analytics-api'

urlpatterns = [
    # List of popular search queries
    path('popular-searches/', api_views.PopularSearchesView.as_view(), name='popular-searches'),

    # List og popular properties
    path('popular-listings/', api_views.PopularListingsView.as_view(), name='popular-listings'),
]
