"""
Initial data load
- Load German cities intro the City table
- Load property types into the PropertyType table
"""

from django.core.management.base import BaseCommand
from common.models import City
from properties.models import PropertyType


class Command(BaseCommand):
    def handle(self, *args, **options):

        self.stdout.write('\n Loading Cities')

        cities = [
            'Berlin', 'Hamburg', 'Munich', 'Cologne', 'Frankfurt',
            'Stuttgart', 'Düsseldorf', 'Leipzig', 'Dresden', 'Nuremberg',
            'Hanover', 'Essen', 'Bremen', 'Bonn', 'Mannheim', 'Heidelberg',
            'Freiburg', 'Karlsruhe', 'Wiesbaden', 'Mainz', 'Aachen', 'Kiel',
            'Dortmund', 'Duisburg', 'Bochum', 'Wuppertal', 'Bielefeld',
            'Münster', 'Magdeburg', 'Potsdam', 'Saarbrücken'
        ]

        self.stdout.write('\n Loading housing')

        property_types = [
            'Apartment',
            'House',
            'Studio',
            'Room',
            'Townhouse',
            'Penthouse'
        ]

        for type_name in property_types:
            obj, created = PropertyType.objects.get_or_create(name=type_name)

        self.stdout.write('\n info:')
        self.stdout.write('   - All citis in the City table ')
        self.stdout.write('   - All housing types in the Property Type ')
