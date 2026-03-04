from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property_listing.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'property_listing', 'property_name', 'user', 'user_name', 'check_in',
                  'check_out', 'status', 'source', 'uid', 'created_at']
        read_only_fields = ['user', 'uid', 'created_at', 'source']

    def validate(self, data):
        # Check for overlapping bookings
        overlapping = Booking.objects.filter(
            property_listing=data['property_listing'],
            check_in__lt=data['check_out'],
            check_out__gt=data['check_in'],
            status__in=['confirmed', 'pending']
        )
        if overlapping.exists():
            raise serializers.ValidationError(
                "This property is already booked for these dates."
            )
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)