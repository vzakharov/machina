from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

# Set up logger
logger = logging.getLogger(__name__)

@csrf_exempt
def supabase_webhook(request):
    """
    Webhook handler for Supabase database events.
    Logs incoming webhook events without requiring DB access.
    """
    if request.method == 'POST':
        try:
            # Parse the incoming webhook payload
            data = json.loads(request.body)
            
            # Log detailed information to console for debugging
            print(f"=====================================")
            print(f"WEBHOOK RECEIVED:")
            print(f"Table: {data.get('table')}")
            print(f"Schema: {data.get('schema')}")
            print(f"Operation: {data.get('operation')}")
            print(f"New Record: {data.get('new_record')}")
            print(f"Old Record: {data.get('old_record')}")
            print(f"=====================================")
            
            # Return a success response
            return JsonResponse({
                'status': 'success',
                'message': f"Webhook for {data.get('operation')} on {data.get('schema')}.{data.get('table')} processed"
            })
            
        except json.JSONDecodeError:
            print("ERROR: Invalid JSON in webhook payload")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are accepted'}, status=405)

def test_webhook(request):
    """
    Simple test endpoint to verify the webhook route is accessible.
    """
    print("===== TEST WEBHOOK ENDPOINT ACCESSED =====")
    return JsonResponse({
        'status': 'success',
        'message': 'Test webhook endpoint is working'
    })
