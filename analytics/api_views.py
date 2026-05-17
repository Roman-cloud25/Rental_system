"""
API views for analytics
"""

from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Count
from .models import SearchHistory
from properties.models import Property
from properties.serializers import PropertyListSerializer


# Return most frequent search keywords
class PopularSearchesView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    # Popular search queries
    def get(self, request):
        popular = (SearchHistory.objects
                   .values('keyword')
                   .annotate(count=Count('keyword'))
                   .order_by('-count')[:20])
        return Response(popular)


# Return listings sorted by views count desc
class PopularListingsView(generics.ListAPIView):
    serializer_class = PropertyListSerializer
    permission_classes = [permissions.AllowAny]

    # Exclude deleted
    def get_queryset(self):
        return Property.objects.exclude(status='deleted').order_by('-views_count')
