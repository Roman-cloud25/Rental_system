"""
API routes for bookings
"""

from django.urls import path
from . import api_views

app_name = 'bookings-api'

urlpatterns = [
    # Create and list bookings
    path('', api_views.BookingListCreateView.as_view(), name='booking-list-create'),

    # Details bookings
    path('<int:pk>/', api_views.BookingDetailView.as_view(), name='booking-detail'),

    # Confirmation bookings
    path('<int:pk>/confirm/', api_views.BookingConfirmRejectView.as_view(), kwargs={'action': 'confirm'},
         name='booking-confirm'),

    # Rejection bookings
    path('<int:pk>/reject/', api_views.BookingConfirmRejectView.as_view(), kwargs={'action': 'reject'},
         name='booking-reject'),
]
