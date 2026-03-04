from django.contrib import admin
from .models import Property, PropertyImage
from .utils import sync_property_calendars
from bookings.models import Booking


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    readonly_fields = ('check_in', 'check_out', 'source', 'uid', 'status')
    can_delete = False


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'order')
    verbose_name_plural = "Gallery Images"


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "owner", "price_per_night", "created_at")
    list_filter = ("city", "created_at", "has_wifi", "has_pool", "has_ac")
    search_fields = ("name", "city", "owner__username")
    
    inlines = [PropertyImageInline, BookingInline]
    
    actions = ["sync_selected_properties"]

    fieldsets = (
        ("Basic Information", {
            'fields': ('owner', 'name', 'description', 'city', 'address')
        }),
        ("Pricing & Amenities", {
            'fields': ('price_per_night', 'beds', 'baths', 'has_wifi', 'has_pool', 'has_ac')
        }),
        ("Legacy Image", {
            'fields': ('image',),
            'classes': ('collapse',),
            'description': 'Use the Gallery Images section below to manage property photos.'
        }),
        ("External Calendar Sync", {
            'fields': ('airbnb_ical_url', 'booking_ical_url'),
            'classes': ('collapse',)
        }),
    )

    def sync_selected_properties(self, request, queryset):
        total = 0
        for property_obj in queryset:
            results = sync_property_calendars(property_obj)
            total += len(results)
        self.message_user(request, f"Sync completed. {total} bookings processed.")

    sync_selected_properties.short_description = "Sync external calendars"


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ("property", "is_primary", "order", "created_at")
    list_filter = ("is_primary", "created_at", "property")
    search_fields = ("property__name", "alt_text")
    ordering = ("property", "order", "created_at")