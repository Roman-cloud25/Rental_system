from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'email', 'name', 'role', 'is_tenant', 'is_landlord', 'is_active')
    list_filter = ('role', 'is_tenant', 'is_landlord', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)