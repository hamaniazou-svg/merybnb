from rest_framework import serializers
from .models import Property, PropertyImage
from bookings.models import Booking


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order', 'created_at']
        read_only_fields = ['created_at']


class BookingNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'source', 'status']


class PropertySerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    bookings = BookingNestedSerializer(many=True, read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    image = serializers.ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = Property
        fields = ['id', 'owner', 'owner_name', 'name', 'description', 'city', 'address',
                  'price_per_night', 'image', 'images', 'primary_image', 'beds', 'baths', 
                  'has_wifi', 'has_pool', 'has_ac', 'bookings', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']

    def get_primary_image(self, obj):
        """Get the primary image or first image in gallery"""
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return PropertyImageSerializer(primary).data
        first_image = obj.images.first()
        if first_image:
            return PropertyImageSerializer(first_image).data
        # Fallback to legacy image field
        if obj.image:
            return {
                'id': None,
                'image': obj.image.url if obj.image else None,
                'alt_text': obj.name,
                'is_primary': True,
                'order': 0
            }
        return None

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)