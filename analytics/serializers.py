"""
Serializers for analytics
"""

from rest_framework import serializers
from .models import SearchHistory, ViewHistory


# Display search history
class SearchHistorySerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = SearchHistory
        fields = ['id', 'keyword', 'user_email', 'searched_at']
        read_only_fields = ['id', 'searched_at']


# Popular search queries
class PopularKeywordSerializer(serializers.Serializer):
    keyword = serializers.CharField()
    count = serializers.IntegerField()


# Display listing view history
class ViewHistorySerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.title', read_only=True)

    class Meta:
        model = ViewHistory
        fields = ['id', 'listing', 'listing_title', 'viewed_at']
        read_only_fields = ['id', 'viewed_at']
