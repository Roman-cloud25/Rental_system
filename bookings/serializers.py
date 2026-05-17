"""
Serializers for Bookings
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Booking


# Bookings for creation, retrieve, updating
class BookingSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)
    nights = serializers.IntegerField(source='nights_count', read_only=True)
    property_price = serializers.DecimalField(source='listing.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'listing', 'listing_title', 'tenant', 'tenant_name',
            'start_date', 'end_date', 'status', 'total_price', 'nights',
            'guests', 'special_requests', 'created_at', 'updated_at', 'property_price'
        ]
        read_only_fields = ['id', 'tenant', 'status', 'total_price', 'created_at', 'updated_at']

    # Validate dates, listing availability active, date overlaps
    def validate(self, data):
        listing = data.get('listing')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Validate active listing availability
        if listing.status != 'active':
            raise serializers.ValidationError("This property is not available for booking.")

        if start_date >= end_date:
            raise serializers.ValidationError("End date must be after start date.")

        if start_date < timezone.now().date():
            raise serializers.ValidationError("Cannot book past dates.")

        # Check for date overlap
        overlapping = Booking.objects.filter(
            listing=listing,
            status__in=['pending', 'confirmed'],
            start_date__lt=end_date,
            end_date__gt=start_date,
        )
        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)

        if overlapping.exists():
            raise serializers.ValidationError("These dates are already booked.")

        return data

    # Auto calculate total price
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['tenant'] = request.user
        nights = (validated_data['end_date'] - validated_data['start_date']).days
        validated_data['total_price'] = nights * validated_data['listing'].price
        return super().create(validated_data)


# Status update confirm, reject
class BookingUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['status']

    def validate_status(self, value):
        allowed = ['confirmed', 'rejected']
        if value not in allowed:
            raise serializers.ValidationError(f"Status can only be set to {', '.join(allowed)}.")
        return value
