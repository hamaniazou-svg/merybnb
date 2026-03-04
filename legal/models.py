from django.db import models
from django.core.validators import EmailValidator
import uuid


class HostApplication(models.Model):
    """
    Model to store host applications for the Merybnb platform.
    Tracks potential hosts and their application status.
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    full_name = models.CharField(
        max_length=255,
        help_text="Host's full name"
    )
    
    email = models.EmailField(
        validators=[EmailValidator()],
        help_text="Contact email address"
    )
    
    property_name = models.CharField(
        max_length=255,
        help_text="Name or description of the property"
    )
    
    city = models.CharField(
        max_length=100,
        help_text="City where the property is located"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Application status"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Application submission date"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update date"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Host Application'
        verbose_name_plural = 'Host Applications'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.property_name} ({self.get_status_display()})"
