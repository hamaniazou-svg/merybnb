from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    property_name = serializers.CharField(source='property_listing.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    guest_name = serializers.CharField(allow_null=True, required=False)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True, allow_null=True)

    class Meta:
        model = Booking
        fields = ['id', 'property_listing', 'property_name', 'user', 'user_name', 'guest_name',
                  'check_in', 'check_out', 'guest_count', 'status', 'source', 'uid', 'created_at', 'total_price']
        read_only_fields = ['user', 'uid', 'created_at', 'source', 'total_price']

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

        # Validate guest count against property capacity
        property_obj = data.get('property_listing')
        guest_count = data.get('guest_count')
        
        if property_obj and guest_count:
            max_capacity = (property_obj.beds or 1) * 2
            if guest_count > max_capacity:
                raise serializers.ValidationError(
                    f"Maximum capacity for this property is {max_capacity} guests. You selected {guest_count}."
                )
        
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)