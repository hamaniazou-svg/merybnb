from django.urls import path
from .views import BookingListAPIView, BookingCreateAPIView, BookingDetailAPIView

urlpatterns = [
    path('', BookingListAPIView.as_view(), name='booking-list'),
    path('create/', BookingCreateAPIView.as_view(), name='booking-create'),
    path('<str:uid>/', BookingDetailAPIView.as_view(), name='booking-detail'),
]