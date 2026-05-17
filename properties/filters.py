"""
Advertisement filters
"""

from django_filters import rest_framework as filters
from django_filters import DateFilter
from .models import Property


# Filter for the Property model
class PropertyFilter(filters.FilterSet):

    # Filter by price min and max
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte', label='Min price (€)')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte', label='Max price (€)')

    # Filter by min and and rooms
    rooms_min = filters.NumberFilter(field_name='rooms', lookup_expr='gte', label='Min rooms')
    rooms_max = filters.NumberFilter(field_name='rooms', lookup_expr='lte', label='Max rooms')

    # Filter by housing type id or name
    property_type = filters.NumberFilter(field_name='property_type__id', label='Housing type (ID)')

    # Filter by city id
    city = filters.NumberFilter(field_name='location__id', label='City (ID)')

    # Filter by status active and inactive
    status = filters.ChoiceFilter(choices=Property.STATUS_CHOICES, label='Status')

    # Filter available
    available_from = filters.DateFilter(field_name='available_from', lookup_expr='gte', label='Available from')

    class Meta:
        model = Property
        fields = ['price_min', 'price_max', 'rooms_min', 'rooms_max', 'property_type', 'city', 'status']