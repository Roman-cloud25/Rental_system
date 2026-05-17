"""
API views for reviews
"""

from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.db.models import Avg
from .models import Review
from .serializers import ReviewSerializer, ReviewUpdateSerializer
from properties.models import Property


# Permission only the autor can edit or delete the review
class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user or request.user.is_staff

# Review list and create review only tenant
class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.all()
        listing_id = self.request.query_params.get('listing')
        user_id = self.request.query_params.get('user')

        if listing_id:
            queryset = queryset.filter(listing_id=listing_id)
        elif user_id and self.request.user.is_staff:
            queryset = queryset.filter(user_id=user_id)
        elif not listing_id and not user_id:
            queryset = queryset.filter(user=self.request.user)

        return queryset.select_related('listing', 'user', 'booking')

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_tenant:
            raise PermissionDenied("Only tenants can leave reviews.")
        serializer.save()

# Author only update, delete review
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Review.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ReviewUpdateSerializer
        return ReviewSerializer
