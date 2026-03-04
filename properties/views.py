from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Prefetch, F
from django.utils.timezone import now
from datetime import datetime, timedelta
import json

from .models import Property, PropertyImage
from bookings.models import Booking
from .serializers import PropertySerializer, PropertyImageSerializer
from bookings.serializers import BookingSerializer


class StandardPageNumberPagination(PageNumberPagination):
    """
    Standard pagination for API endpoints.
    Returns 12 properties per page.
    """
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class PropertyListAPIView(generics.ListCreateAPIView):
    """
    List all properties with search, filter, and pagination.
    Authenticated users can create new properties.
    
    Query Parameters:
        - search: Search by name, city, address, description
        - page: Page number for pagination
        - page_size: Items per page (max 100)
        - city: Filter by city
        - min_price: Minimum price per night
        - max_price: Maximum price per night
        - has_wifi: Filter by WiFi (true/false)
        - has_pool: Filter by pool (true/false)
    """
    
    serializer_class = PropertySerializer
    pagination_class = StandardPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'city', 'address', 'description']
    ordering_fields = ['price_per_night', 'created_at', 'beds', 'baths']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Optimize queries with select_related and prefetch_related.
        Filter by city, price range, and amenities if provided.
        """
        queryset = Property.objects.select_related('owner').prefetch_related(
            Prefetch(
                'images',
                queryset=PropertyImage.objects.filter(is_primary=True)
            )
        ).all()
        
        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price_per_night__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_night__lte=max_price)
        
        # Filter by amenities
        if self.request.query_params.get('has_wifi') == 'true':
            queryset = queryset.filter(has_wifi=True)
        if self.request.query_params.get('has_pool') == 'true':
            queryset = queryset.filter(has_pool=True)
        
        return queryset
    
    def get_permissions(self):
        """
        Allow anyone to read, but require authentication to create.
        """
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def perform_create(self, serializer):
        """Automatically assign the current user as property owner"""
        serializer.save(owner=self.request.user)


class PropertyDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific property.
    
    GET is public (anyone can view).
    PUT/PATCH/DELETE require authentication (owner only).
    
    Response includes:
        - Full property details
        - All images in gallery
        - Primary image designation
        - Related bookings (confirmed/pending dates)
    """
    
    queryset = Property.objects.select_related('owner').prefetch_related(
        'images',
        Prefetch(
            'bookings',
            queryset=Booking.objects.filter(
                status__in=['confirmed', 'pending']
            )
        )
    )
    serializer_class = PropertySerializer
    lookup_field = 'pk'
    
    def get_permissions(self):
        """
        Allow anyone to read, but restrict writes to owners.
        """
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_update(self, serializer):
        """Ensure only owner can update their property"""
        if serializer.instance.owner != self.request.user:
            return Response(
                {'detail': 'You do not have permission to edit this property.'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure only owner can delete their property"""
        if instance.owner != self.request.user:
            return Response(
                {'detail': 'You do not have permission to delete this property.'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()


@api_view(['GET'])
@require_http_methods(["GET"])
def property_availability(request, pk):
    """
    Get availability calendar for a property.
    
    Returns:
        - available_dates: List of dates that are available
        - booked_dates: List of dates that are booked
        - min_date: Earliest available date
        - max_date: Latest available date (30 days from now)
    """
    property_obj = get_object_or_404(Property, pk=pk)
    
    # Get date range (next 30 days)
    today = now().date()
    min_date = today + timedelta(days=1)  # Can't book for today
    max_date = today + timedelta(days=30)
    
    # Get all booked dates
    bookings = Booking.objects.filter(
        property=property_obj,
        check_in__gte=min_date,
        check_out__lte=max_date,
        status__in=['confirmed', 'pending']
    ).values_list('check_in', 'check_out')
    
    # Build list of booked dates
    booked_dates = set()
    for check_in, check_out in bookings:
        current = check_in
        while current < check_out:
            booked_dates.add(str(current))
            current += timedelta(days=1)
    
    # Build list of available dates
    available_dates = []
    current = min_date
    while current <= max_date:
        if str(current) not in booked_dates:
            available_dates.append(str(current))
        current += timedelta(days=1)
    
    return Response({
        'property_id': property_obj.id,
        'property_name': property_obj.name,
        'available_dates': available_dates,
        'booked_dates': list(booked_dates),
        'min_date': str(min_date),
        'max_date': str(max_date),
        'nightly_rate': float(property_obj.price_per_night),
    })


@api_view(['POST'])
def calculate_booking_cost(request, pk):
    """
    Calculate total cost for a booking.
    
    Request body:
        {
            "check_in": "2026-03-15",
            "check_out": "2026-03-20"
        }
    
    Returns:
        {
            "num_nights": 5,
            "nightly_rate": 150.00,
            "total_price": 750.00,
            "currency": "USD"
        }
    """
    property_obj = get_object_or_404(Property, pk=pk)
    
    check_in_str = request.data.get('check_in')
    check_out_str = request.data.get('check_out')
    
    if not check_in_str or not check_out_str:
        return Response(
            {'error': 'Both check_in and check_out dates are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Dates must be in YYYY-MM-DD format.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if check_in >= check_out:
        return Response(
            {'error': 'Check-out must be after check-in.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate nights and total
    delta = check_out - check_in
    num_nights = delta.days
    nightly_rate = float(property_obj.price_per_night)
    total_price = num_nights * nightly_rate
    
    # Check for overlaps
    has_overlap = Booking.objects.filter(
        property=property_obj,
        check_in__lt=check_out,
        check_out__gt=check_in,
        status__in=['confirmed', 'pending']
    ).exists()
    
    return Response({
        'property_id': property_obj.id,
        'property_name': property_obj.name,
        'check_in': str(check_in),
        'check_out': str(check_out),
        'num_nights': num_nights,
        'nightly_rate': nightly_rate,
        'total_price': total_price,
        'currency': 'USD',
        'is_available': not has_overlap,
        'availability_error': 'Property is booked for these dates' if has_overlap else None,
    })


def property_detail_page(request, pk):
    """
    Render the property detail page (detail.html).
    
    Context:
        - property: Property object with all images and bookings
        - images: All PropertyImage objects in order
        - primary_image: Primary image for display
        - booked_dates: JSON list of booked dates for calendar widget
        - nightly_rate: Property nightly rate
        - num_images: Total number of images in gallery
    """
    property_obj = get_object_or_404(
        Property.objects.select_related('owner').prefetch_related('images', 'bookings'),
        pk=pk
    )
    
    # Get all images ordered by display order
    images = property_obj.images.all()
    
    # Get booked dates for calendar
    booked_bookings = Booking.objects.filter(
        property_listing=property_obj,
        status__in=['confirmed', 'pending']
    ).values_list('check_in', 'check_out')
    
    booked_dates = []
    for check_in, check_out in booked_bookings:
        current = check_in
        while current < check_out:
            booked_dates.append(str(current))
            current += timedelta(days=1)
    
    context = {
        'property': property_obj,
        'images': images,
        'primary_image': property_obj.primary_image,
        'booked_dates': json.dumps(booked_dates),
        'nightly_rate': float(property_obj.price_per_night),
        'num_images': images.count(),
        'amenities': {
            'wifi': property_obj.has_wifi,
            'pool': property_obj.has_pool,
            'ac': property_obj.has_ac,
        },
        'booking_form_action': f'/api/bookings/create/',
    }
    
    return render(request, 'detail.html', context)
