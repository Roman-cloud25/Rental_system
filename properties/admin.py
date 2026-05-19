from django.contrib import admin
from .models import Property, PropertyType

@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'location', 'price', 'rooms', 'status', 'owner', 'views_count')
    list_filter = ('status', 'property_type', 'location')
    search_fields = ('title', 'description', 'address')