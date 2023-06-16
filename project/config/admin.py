from django.contrib import admin

from config.models import GlobalConfig


@admin.register(GlobalConfig)
class GlobalConfigAdmin(admin.ModelAdmin):
    list_display = ['id', 'config_name', 'config_value', 'is_active']
    search_fields = ['config_name']
    list_filter = ['is_active']
