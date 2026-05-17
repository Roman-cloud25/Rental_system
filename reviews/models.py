"""
Reviews and ratings
"""

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from properties.models import Property
from bookings.models import Booking


# Review for listing
class Review(models.Model):

    # Relation to listing reviews deleted when listing is removed
    listing = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Property'
    )

    # Relation to user author of the review
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='User'
    )

    # Relation to booking one review per booking
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='review',
        verbose_name='Booking'
    )

    # Rating from 1 to 5
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Rating (1-5)'
    )

    # Review text is optional
    comment = models.TextField(blank=True, verbose_name='Comment')

    # Dates
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        # One user one review booking
        unique_together = [['listing', 'user', 'booking']]

    def __str__(self):
        return f"Review for {self.listing.title} - {self.rating}"

    # Validation booking
    def clean(self):

        if self.listing.owner == self.user:
            raise ValidationError("You cannot review your own property.")

        if self.booking.status != 'completed':
            raise ValidationError("You can only review completed bookings.")

        if self.booking.tenant != self.user:
            raise ValidationError("This booking does not belong to you.")

        if self.booking.listing != self.listing:
            raise ValidationError("This booking is not for this property.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)