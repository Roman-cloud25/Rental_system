"""
API views for booking
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Booking
from .serializers import BookingSerializer, BookingUpdateSerializer

# Permission rules
class IsTenantOrLandlord(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        # Allow all
        if request.user.is_staff:
            return True
        # GET allow tenant and landlord
        if request.method in permissions.SAFE_METHODS:
            return obj.tenant == request.user or obj.listing.owner == request.user
        # PUT/PATCH/DELETE: tenant can cancel only their booking
        if request.method == 'DELETE':
            return obj.tenant == request.user and obj.status in ['pending', 'confirmed']


# GET: tenant sees own, landlord sees booking of their listings, admin sees all
class BookingListCreateView(generics.ListCreateAPIView):

    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    #
    def get_queryset(self):
        # Sees all booking
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()

        # Landlord sees bookings of their own listings
        if user.is_landlord:
            return Booking.objects.filter(listing__owner=user)

        # Tenant sees their own bookings
        return Booking.objects.filter(tenant=user)


    # Booking creation tenant only, cannot book own listing
    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_tenant:
            raise PermissionDenied("Only tenants can create bookings.")
        serializer.save()

        listing = serializer.validated_data.get('listing')
        if listing.owner == user:
            raise PermissionDenied("You cannot book your own property.")

        # Save booking tenant taken from request, not client input for prevent ID spoofing
        serializer.save(tenant=user)


# Booking detail view GET, DELETE, PATCH
class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):

    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantOrLandlord]
    http_method_names = ['get', 'delete']

    # Cancel booking with time-limit check 24h before start
    def perform_destroy(self, instance):
        try:
            instance.cancel()
        except ValidationError as e:
            raise PermissionDenied(str(e))


# PATCH actions for landlord
class BookingConfirmRejectView(generics.UpdateAPIView):

    queryset = Booking.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    # PATCH requests for 'confirm' and 'reject'
    def patch(self, request, *args, **kwargs):
        booking = self.get_object()

        # Permission check only listing owner or admin allowed
        if booking.listing.owner != request.user and not request.user.is_staff:
            raise PermissionDenied("Only the landlord can confirm or reject.")

        # 'confirm' 'reject' from URL
        action = kwargs.get('action')

        try:
            if action == 'confirm':
                booking.confirm()
                message = "Booking confirmed"
            elif action == 'reject':
                booking.reject()
                message = "Booking rejected"
            else:
                return Response({'error': 'Invalid action. Use confirm or reject.'},
                                status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'status': booking.status,
            'message': message
        }, status=status.HTTP_200_OK)
