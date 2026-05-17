"""
Advertisement models
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from common.models import City


# Type of housing
class PropertyType(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Name of the type of housing'
    )

    class Meta:
        db_table = 'property_types'
        verbose_name = 'Type of housing'
        verbose_name_plural = 'Types of housing'

    def __str__(self):
        return self.name

# Announcement of housing for rent
class Property(models.Model):

    # Announcement status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('rented', 'Rented'),
        ('deleted', 'Deleted'),
    ]

    # Main fields
    title = models.CharField(
        max_length=200,
        verbose_name='Headline')

    description = models.TextField(
        verbose_name='Description')

    # City
    location = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name='properties',
        verbose_name='City'
    )

    # Full address
    address = models.CharField(
        max_length=255,
        verbose_name='Full address')

    # Price per nignt
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Price per night (€)'
    )

    # Number of rooms
    rooms = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name='Number of rooms'
    )

    # Type of housing
    property_type = models.ForeignKey(
        PropertyType,
        on_delete=models.PROTECT,
        related_name='properties',
        verbose_name='Type of housing'
    )

    # Additional fields
    available_from = models.DateField(
        null=True,
        blank=True,
        verbose_name='Available from'
    )

    min_rental_period = models.IntegerField(
        default=1,
        verbose_name='Minimum rental period nights'
    )

    # Images
    images = models.JSONField(
        default=list,
        verbose_name='Images',
        help_text='List of images URL in AWS S3'
    )

    # Owner
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties',
        limit_choices_to={'is_landlord': True},
        verbose_name='Landlord'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )

    # Dates
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date of creation')

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Date of update')

    # Analytics
    views_count = models.IntegerField(
        default=0,
        verbose_name='Number of views')

    # Soft delete
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Deletion date')

    class Meta:
        db_table = 'properties'
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['location']),
            models.Index(fields=['price']),
            models.Index(fields=['rooms']),
        ]

    def __str__(self):
        return f"{self.title} - {self.location.name}"

    # Soft delete do not delete from the Database
    def soft_delete(self):
        self.status = 'deleted'
        self.deleted_at = timezone.now()
        self.save()

    # Restoring from soft delete
    def restore(self):
        self.status = 'inactive'
        self.deleted_at = None
        self.save()

    # View counter
    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])