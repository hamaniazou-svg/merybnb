"""
Booking models for external and internal reservations.

Stores bookings synced from Airbnb / Booking.com or created manually.
"""

from django.db import models
from django.contrib.auth.models import User
from properties.models import Property
import uuid
from datetime import date


class Booking(models.Model):
    """
    Represents a reservation linked to a property.

    Uses UID from external calendar sources to prevent duplicates.
    Includes automatic price calculation based on check-in/check-out dates.
    """

    class SourceChoices(models.TextChoices):
        AIRBNB = "airbnb", "Airbnb"
        BOOKING = "booking", "Booking.com"
        WEBSITE = "website", "Website"

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending Confirmation"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"

    property_listing = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="bookings",
        help_text="Property being booked"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings",
        null=True,
        blank=True,
        help_text="User who made the booking"
    )

    check_in = models.DateField(
        null=True,
        blank=True,
        help_text="Check-in date"
    )
    check_out = models.DateField(
        null=True,
        blank=True,
        help_text="Check-out date"
    )

    guest_count = models.PositiveIntegerField(
        default=1,
        null=True,
        blank=True,
        help_text="Number of guests for this booking"
    )

    source = models.CharField(
        max_length=20,
        choices=SourceChoices.choices,
        default="website",
        help_text="Where this booking came from"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default="pending",
        help_text="Current booking status"
    )

    # Guest information for external bookings
    guest_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Guest name for external bookings"
    )

    guest_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Guest email for communication"
    )

    uid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Unique identifier for tracking across systems"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["check_in"]
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        indexes = [
            models.Index(fields=['property_listing', 'check_in']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.property_listing.name} | {self.check_in} → {self.check_out} ({self.status})"

    @property
    def num_nights(self):
        """Calculate number of nights booked"""
        if self.check_in and self.check_out:
            delta = self.check_out - self.check_in
            return max(1, delta.days)
        return 0

    @property
    def total_price(self):
        """
        Automatic price calculation.
        Multiplies nightly rate by number of nights.
        Returns decimal amount.
        """
        if self.num_nights > 0 and self.property_listing:
            return self.property_listing.price_per_night * self.num_nights
        return 0

    @property
    def is_overlapping(self):
        """
        Check if this booking overlaps with existing confirmed/pending bookings.
        Useful for validation on booking creation.
        """
        if not self.check_in or not self.check_out:
            return False

        overlapping = Booking.objects.filter(
            property_listing=self.property_listing,
            check_in__lt=self.check_out,
            check_out__gt=self.check_in,
            status__in=['confirmed', 'pending']
        ).exclude(id=self.id)

        return overlapping.exists()

    def clean(self):
        """
        Validate booking data.
        Called before saving in views.
        """
        from django.core.exceptions import ValidationError

        if self.check_in and self.check_out:
            if self.check_in >= self.check_out:
                raise ValidationError("Check-out must be after check-in")

            if self.check_in < date.today():
                raise ValidationError("Cannot book past dates")

            if self.is_overlapping:
                raise ValidationError(
                    "Property is already booked for these dates"
                )