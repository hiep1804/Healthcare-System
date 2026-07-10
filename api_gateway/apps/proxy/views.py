import requests
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

SERVICE_PORTS = {
    'patients': 8002,
    'providers': 8003,
    'specialties': 8003, # Provider service
    'clinics': 8003, # Provider service
    'appointments': 8004,
    'schedules': 8004,
    'consultations': 8005,
    'medical-records': 8006,
    'allergies': 8006,
    'medications': 8006,
    'conditions': 8006,
    'notifications': 8007,
    'notification-templates': 8007,
    'audit': 8008,
    'plans': 8009,
    'subscriptions': 8009,
    'insurance-policies': 8010,
    'claims': 8010,
}

class ProxyView(APIView):
    """
    Reverse Proxy that forwards requests to the appropriate microservice
    based on the URL path.
    """
    permission_classes = [AllowAny]

    def _proxy_request(self, request, service_name, path):
        port = SERVICE_PORTS.get(service_name)
        if not port:
            return JsonResponse({'error': 'Service not found'}, status=404)

        # Construct target URL
        if path:
            target_url = f'http://127.0.0.1:{port}/api/v1/{service_name}/{path}'
        else:
            target_url = f'http://127.0.0.1:{port}/api/v1/{service_name}'
        
        # Prepare headers (forward authorization)
        headers = {key: value for (key, value) in request.headers.items() if key.lower() not in ['host', 'content-length']}
        
        # Determine data based on request method
        data = request.body if request.method in ['POST', 'PUT', 'PATCH'] else None
        
        try:
            # Forward the request
            response = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=data,
                params=request.GET
            )
            
            # Return the response
            django_response = HttpResponse(
                content=response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type', 'application/json')
            )
            return django_response
            
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': 'Upstream service unavailable', 'details': str(e)}, status=503)

    def get(self, request, service_name, path=''):
        return self._proxy_request(request, service_name, path)

    def post(self, request, service_name, path=''):
        return self._proxy_request(request, service_name, path)

    def put(self, request, service_name, path=''):
        return self._proxy_request(request, service_name, path)
        
    def patch(self, request, service_name, path=''):
        return self._proxy_request(request, service_name, path)

    def delete(self, request, service_name, path=''):
        return self._proxy_request(request, service_name, path)

    def options(self, request, service_name, path=''):
        return self._proxy_request(request, service_name, path)
