from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('property_listing', 'user', 'check_in', 'check_out', 'status', 'source')
    list_filter = ('status', 'source', 'created_at', 'user')
    search_fields = ('property_listing__name', 'user__username', 'uid')
    ordering = ('-check_in',)
    readonly_fields = ('uid', 'created_at', 'user')
    fieldsets = (
        ('Booking Information', {
            'fields': ('property_listing', 'user', 'check_in', 'check_out', 'status')
        }),
        ('Source & Tracking', {
            'fields': ('source', 'uid', 'created_at')
        }),
    )