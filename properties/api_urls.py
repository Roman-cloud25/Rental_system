"""
API routes for listings
"""

from django.urls import path
from . import api_views

app_name = 'properties-api'

urlpatterns = [
    # List and Creation
    path('', api_views.PropertyListCreateView.as_view(), name='property-list-create'),

    # Details, Update, Delete
    path('<int:pk>/', api_views.PropertyDetailView.as_view(), name='property-detail'),

    # Switches status between active and inactive
    path('<int:pk>/toggle_status/', api_views.TogglePropertyStatusView.as_view(), name='property-toggle-status'),
]