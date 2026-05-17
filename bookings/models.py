"""
Booking Model
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from properties.models import Property


# Booking
class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    # Booking removed when listing is deleted
    listing = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Property'
    )

    # Booking made by tenant
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Tenant'
    )

    # Date
    start_date = models.DateField(verbose_name='Check-in date')
    end_date = models.DateField(verbose_name='Check-out date')

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Total price (€)'
    )

    # Guests count
    guests = models.PositiveIntegerField(default=1, verbose_name='Number of guests')

    # Special requests
    special_requests = models.TextField(blank=True, verbose_name='Special requests')

    # Creation date
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')

    # Update date
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    # Booking confirmation by landlord only 'pending' bookings can be confirmed status becomes 'confirmed'
    def confirm(self):

        if self.status != 'pending':
            from django.core.exceptions import ValidationError
            raise ValidationError("Only pending bookings can be confirmed.")
        self.status = 'confirmed'
        self.save(update_fields=['status'])

    # Prevent overlapping bookings
    class Meta:
        db_table = 'bookings'
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-created_at']

    # Booking rejection by landlord only 'pending' bookings can be rejected status becomes 'rejected'
    def reject(self):

        if self.status != 'pending':
            from django.core.exceptions import ValidationError
            raise ValidationError("Only pending bookings can be rejected.")
        self.status = 'rejected'
        self.save(update_fields=['status'])

    def __str__(self):
        return f"{self.listing.title} - {self.tenant.email} ({self.start_date} to {self.end_date})"

    # Validation checks date order no past start date and no overlapping bookings
    def clean(self):

        if self.start_date >= self.end_date:
            raise ValidationError({'end_date': 'Check-out date must be after check-in date.'})

        if self.start_date < timezone.now().date():
            raise ValidationError({'start_date': 'Cannot book past dates.'})

        # Check date overlap with active bookings
        overlapping = Booking.objects.filter(
            listing=self.listing,
            status__in=['pending', 'confirmed'],
            start_date__lt=self.end_date,
            end_date__gt=self.start_date,
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError('These dates are already booked.')

    # Validation before saving
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def nights_count(self):
        return (self.end_date - self.start_date).days

    def calculate_total_price(self):
        if self.listing:
            return self.nights_count * self.listing.price
        return 0

    # Booking cancellation
    def cancel(self):
        if self.status in ['pending', 'confirmed']:
            # We verify that at least 24 hours remain before check-in
            if self.start_date > timezone.now().date():
                self.status = 'cancelled'
                self.save(update_fields=['status'])
                return True
            else:
                raise ValidationError('Cannot cancel less than 24 hours before check-in.')
        return False
