from django.contrib import admin
from .models import HostApplication


@admin.register(HostApplication)
class HostApplicationAdmin(admin.ModelAdmin):
    """Admin interface for Host Applications"""
    list_display = ('full_name', 'email', 'property_name', 'city', 'status', 'created_at')
    list_filter = ('status', 'city', 'created_at')
    search_fields = ('full_name', 'email', 'property_name', 'city')
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Application Info', {
            'fields': ('id', 'full_name', 'email', 'property_name', 'city')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-created_at',)
