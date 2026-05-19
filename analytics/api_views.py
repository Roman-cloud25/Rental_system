"""
API views for analytics
"""

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count, Sum, Avg
from .models import SearchHistory
from properties.models import Property
from properties.serializers import PropertyListSerializer
from bookings.models import Booking
from reviews.models import Review


# Return most frequent search keywords
class PopularSearchesView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    # Popular search queries
    def get(self, request):
        popular = (SearchHistory.objects
                   .values('keyword')
                   .annotate(count=Count('keyword'))
                   .order_by('-count')[:20])
        return Response(popular)


# Return listings sorted by views count desc
class PopularListingsView(generics.ListAPIView):
    serializer_class = PropertyListSerializer
    permission_classes = [permissions.AllowAny]

    # Exclude deleted
    def get_queryset(self):
        return Property.objects.exclude(status='deleted').order_by('-views_count')


# Landlord statistics view
class LandlordStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Get statistics for landlord (views, bookings, reviews, rating)
    def get(self, request):
        user = request.user

        # Check if user is landlord or admin
        if not user.is_landlord and not user.is_staff:
            raise PermissionDenied("Only landlords can view statistics")

        # Get all properties owned by this landlord (exclude deleted)
        properties = Property.objects.filter(owner=user).exclude(status='deleted')

        # If no properties, return zeros
        if not properties.exists():
            return Response({
                'total_views': 0,
                'total_bookings': 0,
                'total_reviews': 0,
                'avg_rating': 0.0,
                'properties_count': 0,
                'properties': []
            })

        # Calculate total views (sum of views_count)
        total_views = properties.aggregate(total=Sum('views_count'))['total'] or 0

        # Calculate total bookings
        total_bookings = Booking.objects.filter(listing__in=properties).count()

        # Calculate total reviews
        total_reviews = Review.objects.filter(listing__in=properties).count()

        # Calculate average rating across all properties
        avg_rating = Review.objects.filter(listing__in=properties).aggregate(
            avg=Avg('rating')
        )['avg'] or 0.0

        # Detailed statistics for each property
        properties_stats = []
        for prop in properties:
            prop_bookings = Booking.objects.filter(listing=prop).count()
            prop_reviews = Review.objects.filter(listing=prop).count()
            prop_avg_rating = prop.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

            properties_stats.append({
                'id': prop.id,
                'title': prop.title,
                'views_count': prop.views_count,
                'bookings_count': prop_bookings,
                'reviews_count': prop_reviews,
                'avg_rating': round(prop_avg_rating, 2)
            })

        # Sort by views count (most popular first)
        properties_stats.sort(key=lambda x: x['views_count'], reverse=True)

        return Response({
            'total_views': total_views,
            'total_bookings': total_bookings,
            'total_reviews': total_reviews,
            'avg_rating': round(avg_rating, 2),
            'properties_count': properties.count(),
            'properties': properties_stats[:10]  # Top 10 properties
        })