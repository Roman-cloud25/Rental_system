"""
API routes for reviews
"""

from django.urls import path
from . import api_views

app_name = 'reviews-api'

urlpatterns = [
    # List and creation
    path('', api_views.ReviewListCreateView.as_view(), name='review-list-create'),

    # Details, update, delete
    path('<int:pk>/', api_views.ReviewDetailView.as_view(), name='review-detail'),

]