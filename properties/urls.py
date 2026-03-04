from django.urls import path
from .views import (
    PropertyListAPIView, 
    PropertyDetailAPIView,
    property_availability,
    calculate_booking_cost,
)

urlpatterns = [
    path('', PropertyListAPIView.as_view(), name='property-list'),
    path('<int:pk>/', PropertyDetailAPIView.as_view(), name='property-detail'),
    path('<int:pk>/availability/', property_availability, name='property-availability'),
    path('<int:pk>/calculate-cost/', calculate_booking_cost, name='calculate-cost'),
]