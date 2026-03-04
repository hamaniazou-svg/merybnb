from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import HostApplication


@require_http_methods(["POST"])
@csrf_exempt
def submit_host_application(request):
    """
    Handle host application submissions from the form.
    Returns JSON response with status.
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['full_name', 'email', 'property_name', 'city']
        if not all(field in data for field in required_fields):
            return JsonResponse({
                'success': False,
                'message': 'Missing required fields'
            }, status=400)
        
        # Create application
        application = HostApplication.objects.create(
            full_name=data['full_name'],
            email=data['email'],
            property_name=data['property_name'],
            city=data['city'],
            status='pending'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Thank you for your interest! We will contact you within 24 hours.',
            'application_id': str(application.id)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }, status=500)
