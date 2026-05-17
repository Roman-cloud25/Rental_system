"""
Serializers for reviews
"""

from rest_framework import serializers
from .models import Review


# Main serializer for reviews
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    listing_location = serializers.CharField(source='listing.location.name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'listing', 'listing_title', 'listing_location',
            'user', 'user_name', 'booking', 'rating', 'comment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


    # Validate booking
    def validate(self, data):

        booking = data.get('booking')
        user = self.context['request'].user

        if booking.tenant != user:
            raise serializers.ValidationError("You can only review your own bookings.")

        if booking.status != 'completed':
            raise serializers.ValidationError("You can only review completed bookings.")

        if Review.objects.filter(booking=booking).exists():
            raise serializers.ValidationError("A review already exists for this booking.")

        return data

    # Auto fill user and listing
    def create(self, validated_data):

        request = self.context['request']
        validated_data['user'] = request.user
        booking = validated_data['booking']
        validated_data['listing'] = booking.listing
        return super().create(validated_data)


# Serializer for updating a review
class ReviewUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['rating', 'comment']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value