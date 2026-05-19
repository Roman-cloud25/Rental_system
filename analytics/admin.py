from django.contrib import admin
from .models import SearchHistory, ViewHistory

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'keyword', 'user', 'searched_at')
    list_filter = ('searched_at',)
    search_fields = ('keyword', 'user__email')

@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'listing', 'user', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('listing__title', 'user__email')