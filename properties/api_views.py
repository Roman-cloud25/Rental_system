"""
API views for advertisements
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db import models
from django.db.models import Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Property
from .serializers import PropertySerializer, PropertyListSerializer
from .filters import PropertyFilter


# Owner only permissions for updates and deletions public read access
class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Permits GET, HEAD, OPTIONS anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only thr owner or administrator can make changes
        return obj.owner == request.user or request.user.is_staff


# Lists all active, non-deleted properties and allows landlords to create new ones, search, filters, sorting
class PropertyListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # Exclude deleted and load related objects
    queryset = Property.objects.exclude(status='deleted').select_related('location', 'property_type', 'owner')

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    # Filtration class
    filterset_class = PropertyFilter
    search_fields = [
        'title',
        'description',
        'location__name']

    ordering_fields = [
        'price',
        'created_at',
        'views_count',
        'reviews_count',
    ]
    ordering = ['-created_at']

    # Review count for popular
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            reviews_count=models.Count('reviews'),
        )
        return queryset

    # List serializer for GET
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PropertyListSerializer
        return PropertySerializer

    # Automatically assigns the current user as the owner on creation
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_landlord:
            raise PermissionDenied("Only landlords can create listings")
        serializer.save(owner=user)

    # Save search query to history only for authenticated users
    def list(self, request, *args, **kwargs):
        search_param = request.query_params.get('search')
        if search_param and request.user.is_authenticated:
            from analytics.models import SearchHistory
            SearchHistory.objects.create(user=request.user, keyword=search_param)
        return super().list(request, *args, **kwargs)


# Detail view with update and soft delete
class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # Increment views and log unique view
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views()
        if request.user.is_authenticated:
            from analytics.models import ViewHistory
            ViewHistory.record_view(request.user, instance)

        # ViewHistory.objects.create(listing=instance, user=request.user if request.user.is_authenticated else None)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # Soft delete
    def perform_destroy(self, instance):
        instance.soft_delete()


# Switches ststus between active and inactive
class TogglePropertyStatusView(generics.UpdateAPIView):
    queryset = Property.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'active':
            instance.status = 'inactive'
        else:
            instance.status = 'active'
        instance.save(update_fields=['status'])
        return Response({'status': instance.status, 'message': 'Status updated'})