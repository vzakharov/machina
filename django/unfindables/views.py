from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
import json
import logging

# Set up logger
logger = logging.getLogger(__name__)

@csrf_exempt
def supabase_webhook(request: HttpRequest):
    """
    Webhook handler for Supabase database events.
    Logs incoming webhook events without requiring DB access.
    """
    logger.info("=============== WEBHOOK REQUEST RECEIVED ===============")
    logger.info(f"Request Method: {request.method}")
    logger.info(f"Request Headers: {dict(request.headers)}")
    logger.info(f"Request Path: {request.path}")
    logger.info(f"Request META: {request.META.get('REMOTE_ADDR')}")
    
    if request.method == 'POST':
        try:
            # Parse the incoming webhook payload
            data = json.loads(request.body)
            
            # Log detailed information to console for debugging
            logger.info(f"=====================================")
            logger.info(f"WEBHOOK PAYLOAD:")
            logger.info(f"Table: {data.get('table')}")
            logger.info(f"Schema: {data.get('schema')}")
            logger.info(f"Operation: {data.get('type')}")
            logger.info(f"New Record: {data.get('record')}")
            logger.info(f"Old Record: {data.get('old_record')}")
            logger.info(f"Raw Data: {data}")
            logger.info(f"=====================================")
            
            # Return a success response
            return JsonResponse({
                'status': 'success',
                'message': f"Webhook for {data.get('operation')} on {data.get('schema')}.{data.get('table')} processed"
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"ERROR: Invalid JSON in webhook payload: {e}")
            logger.error(f"Request body: {request.body}")
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"ERROR in webhook processing: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Only POST requests are accepted'}, status=405)

def test_webhook(request: HttpRequest):
    """
    Simple test endpoint to verify the webhook route is accessible.
    """
    print("===== TEST WEBHOOK ENDPOINT ACCESSED =====")
    return JsonResponse({
        'status': 'success',
        'message': 'Test webhook endpoint is working'
    })
