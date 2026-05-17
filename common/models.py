"""
Directories cities Germany
"""

from django.db import models


# Model of a Germany city
class City(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='City name'
    )

    class Meta:
        db_table = 'cities'
        verbose_name = 'City'
        verbose_name_plural = 'Cities'
        ordering = ['name']

    def __str__(self):
        return self.name