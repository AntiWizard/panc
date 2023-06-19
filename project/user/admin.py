from django.contrib import admin

from user.models import User, UserSession


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'wallet_address', 'is_active', 'created_at']
    search_fields = ['wallet_address']
    list_filter = ['is_active']


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'session_id', 'user', 'last_login', 'is_active', 'created_at']
    search_fields = ['session_id', 'user']
    list_filter = ['is_active']
