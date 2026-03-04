"""
URL configuration for merybnb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from bookings.views import BookingListAPIView
from django.conf import settings
from django.conf.urls.static import static
from properties.views import PropertyListAPIView, property_detail_page

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Home page
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    
    # Template pages
    path('booking-success.html', TemplateView.as_view(template_name='booking-success.html'), name='booking-success'),
    path('become-host.html', TemplateView.as_view(template_name='become-host.html'), name='become-host'),
    path('my-bookings.html', TemplateView.as_view(template_name='my-bookings.html'), name='my-bookings'),
    path('login.html', TemplateView.as_view(template_name='login.html'), name='login'),
    
    path('admin/', admin.site.urls),
    
    # Property detail page (HTML rendering)
    path('properties/<int:pk>/book/', property_detail_page, name='property-detail-page'),
    
    # App URLs (API endpoints)
    path('api/properties/', include('properties.urls')),
    path('api/bookings/', include('bookings.urls')),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]


# أضف هذا في نهاية قائمة الـ urlpatterns
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)