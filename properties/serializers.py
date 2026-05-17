"""
Advert serializers
"""

from rest_framework import serializers
from .models import Property, PropertyType
from common.models import City

# Main serializer for the Property model
class PropertySerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='location.name', read_only=True)
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)
    owner_name = serializers.CharField(source='owner.name', read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'description', 'location', 'city_name',
            'address', 'price', 'rooms', 'property_type', 'property_type_name',
            'available_from', 'min_rental_period', 'images',
            'owner', 'owner_name', 'status', 'created_at', 'updated_at', 'views_count'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'views_count', 'city_name', 'property_type_name', 'owner_name']

    # Validate price
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be adove 0")
        return value

    # Validate number of rooms
    def validate_rooms(self, value):
        if value <= 0:
            raise serializers.ValidationError("Rooms must be greater than 0")
        return value

# Compact serializer used in property listings
class PropertyListSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='location.name', read_only=True)
    property_type_name = serializers.CharField(source='property_type.name', read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'city_name', 'address', 'price', 'rooms', 'property_type_name', 'status',
            'created_at', 'views_count'
        ]