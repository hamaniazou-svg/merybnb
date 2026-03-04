from django.urls import path
from . import views

app_name = 'legal'

urlpatterns = [
    path('host-application/', views.submit_host_application, name='submit_host_application'),
]
