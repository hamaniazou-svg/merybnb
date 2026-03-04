from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from datetime import datetime
import uuid


class Property(models.Model):
    """
    Property listing model for the Merybnb platform.
    
    Supports multi-image galleries and S3 storage for images.
    Owner-based multi-tenancy for SaaS scalability.
    """
    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='properties',
        null=True,
        blank=True
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Property name (e.g., 'Luxury Beachfront Villa')"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the property"
    )
    
    city = models.CharField(
        max_length=100,
        default="Meknes",
        help_text="City where property is located"
    )
    
    address = models.TextField(
        blank=True,
        help_text="Full street address of the property"
    )
    
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Nightly rate in USD"
    )
    
    # Legacy image field - S3 compatible via storages backend
    image = models.ImageField(
        upload_to='property_images/',
        blank=True,
        null=True,
        help_text="Primary property image (auto-synced to S3 if configured)"
    )
    
    # Property features
    beds = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of bedrooms"
    )
    
    baths = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of bathrooms"
    )
    
    has_wifi = models.BooleanField(
        default=True,
        help_text="Does property have WiFi?"
    )
    
    has_pool = models.BooleanField(
        default=False,
        help_text="Does property have a swimming pool?"
    )
    
    has_ac = models.BooleanField(
        default=True,
        help_text="Does property have air conditioning?"
    )
    
    # External calendar sync for Airbnb/Booking.com
    airbnb_ical_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Airbnb iCalendar sync URL for availability"
    )
    
    booking_ical_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Booking.com iCalendar sync URL for availability"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Property"
        verbose_name_plural = "Properties"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['city']),
        ]
    
    def __str__(self):
        return f"{self.name} by {self.owner.username if self.owner else 'Unknown'}"
    
    @property
    def primary_image(self):
        """Get primary image from gallery, fallback to legacy image field"""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image
        first_image = self.images.first()
        if first_image:
            return first_image.image
        return self.image
    
    @property
    def image_count(self):
        """Get total number of images in gallery"""
        return self.images.count()
    
    def get_available_dates(self):
        """
        Get list of dates that are booked.
        Useful for calendar widgets on frontend.
        """
        from bookings.models import Booking
        from datetime import date, timedelta
        
        bookings = Booking.objects.filter(
            property=self,
            status__in=['confirmed', 'pending']
        ).values_list('check_in', 'check_out')
        
        booked_dates = []
        for check_in, check_out in bookings:
            current = check_in
            while current < check_out:
                booked_dates.append(current)
                current += timedelta(days=1)
        return booked_dates


class PropertyImage(models.Model):
    """
    Gallery images for properties.
    
    Supports unlimited images per property with S3 storage.
    Enables professional multi-image display on detail pages.
    """
    
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images',
        help_text="Property this image belongs to"
    )
    
    image = models.ImageField(
        upload_to='property_images/%Y/%m/',
        help_text="Image file (auto-synced to S3 if configured)"
    )
    
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Accessibility alt text for image"
    )
    
    is_primary = models.BooleanField(
        default=False,
        help_text="Use as thumbnail/primary image in listings"
    )
    
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order in gallery (0 = first)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Property Image"
        verbose_name_plural = "Property Images"
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['property', 'order']),
        ]
    
    def save(self, *args, **kwargs):
        """Enforce only one primary image per property"""
        if self.is_primary:
            PropertyImage.objects.filter(
                property=self.property,
                is_primary=True
            ).update(is_primary=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.property.name} - Image {self.order + 1}"

