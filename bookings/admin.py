from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'tenant', 'start_date', 'end_date', 'status', 'total_price')
    list_filter = ('status',)
    search_fields = ('listing__title', 'tenant__email')