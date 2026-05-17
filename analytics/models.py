"""
Analytics models
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from properties.models import Property


# User search history
class SearchHistory(models.Model):
    keyword = models.CharField(max_length=255, verbose_name='Search keyword')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history',
        verbose_name='User'
    )
    searched_at = models.DateTimeField(auto_now_add=True, verbose_name='Searched at')

    class Meta:
        db_table = 'search_history'
        verbose_name = 'Search History'
        verbose_name_plural = 'Search Histories'
        ordering = ['-searched_at']
        indexes = [
            models.Index(fields=['keyword']),
            models.Index(fields=['user', 'searched_at']),
        ]

    def __str__(self):
        return f"{self.user.email} searched '{self.keyword}' at {self.searched_at}"


# History of listing views
class ViewHistory(models.Model):
    listing = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='views_history',
        verbose_name='Property'
    )
    # Create entry only for authenticated users
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='view_history',
        verbose_name='User'
    )
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name='Viewed at')

    class Meta:
        db_table = 'view_history'
        verbose_name = 'View History'
        verbose_name_plural = 'View Histories'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['listing', 'user', 'viewed_at']),
        ]

    def __str__(self):
        return f"{self.user.email} viewed {self.listing.title} at {self.viewed_at}"

    # Record view if no user view in the last 24h
    @classmethod
    def record_view(cls, user, listing):
        one_day_ago = timezone.now() - timezone.timedelta(days=1)
        exists = cls.objects.filter(user=user, listing=listing, viewed_at__gte=one_day_ago).exists()
        if not exists:
            cls.objects.create(user=user, listing=listing)
            return True
        return False
