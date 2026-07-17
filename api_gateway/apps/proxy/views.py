import requests
import jwt
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

SERVICE_PORTS = {
    'auth': 8001,
    'users': 8001,
    'patients': 8002,
    'providers': 8003,
    'specialties': 8003,
    'clinics': 8003,
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

SERVICE_DOCKER_HOSTS = {
    'auth': 'identity_service',
    'users': 'identity_service',
    'patients': 'patient_service',
    'providers': 'provider_service',
    'specialties': 'provider_service',
    'clinics': 'provider_service',
    'appointments': 'appointment_service',
    'schedules': 'appointment_service',
    'consultations': 'consultation_service',
    'medical-records': 'medical_record_service',
    'allergies': 'medical_record_service',
    'medications': 'medical_record_service',
    'conditions': 'medical_record_service',
    'notifications': 'notification_service',
    'notification-templates': 'notification_service',
    'audit': 'audit_service',
    'plans': 'subscription_service',
    'subscriptions': 'subscription_service',
    'insurance-policies': 'insurance_service',
    'claims': 'insurance_service',
}

# Route to roles mapping
# Format: { service_name: { HTTP_METHOD: [allowed_roles] } }
# Empty list [] means ANY authenticated user.
# '*' means public, no authentication required.
ROUTE_PERMISSIONS = {
    'auth': '*',
    'users': {
        'GET': [], # ANY authenticated (for /users/me), downstream will enforce details
        'PATCH': [], 
        'POST': ['ADMIN'],
        'DELETE': ['ADMIN'],
    },
    'patients': {
        'GET': ['PATIENT', 'DOCTOR', 'ADMIN'],
        'POST': ['PATIENT', 'ADMIN'],
        'PUT': ['PATIENT', 'ADMIN'],
        'PATCH': ['PATIENT', 'ADMIN'],
        'DELETE': ['ADMIN'],
    },
    'providers': '*', # Public to view doctors
    'specialties': '*', 
    'clinics': '*',
    'appointments': {
        'GET': [], # Any authenticated
        'POST': ['PATIENT', 'ADMIN'],
        'PUT': ['PATIENT', 'DOCTOR', 'ADMIN'],
        'PATCH': ['PATIENT', 'DOCTOR', 'ADMIN'],
        'DELETE': ['ADMIN'],
    },
    'consultations': {
        'GET': [], 
        'POST': ['DOCTOR'],
        'PUT': ['DOCTOR'],
        'PATCH': ['DOCTOR'],
    },
    'medical-records': {
        'GET': ['PATIENT', 'DOCTOR', 'ADMIN'],
        'POST': ['DOCTOR', 'ADMIN'],
        'PUT': ['DOCTOR', 'ADMIN'],
        'PATCH': ['DOCTOR', 'ADMIN'],
    },
}

class ProxyView(APIView):
    """
    Reverse Proxy that forwards requests to the appropriate microservice
    based on the URL path.
    Also handles Authentication and Route-to-Roles Authorization.
    """
    permission_classes = [AllowAny]

    def _authenticate_and_authorize(self, request, service_name, method):
        permissions = ROUTE_PERMISSIONS.get(service_name)
        
        # If explicitly marked as '*', public access
        if permissions == '*':
            return None, None # user_id, roles

        # Otherwise, requires authentication
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'error': {'code': 'UNAUTHORIZED', 'message': 'Authentication required.'}}, status=401), None

        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": True},
            )
            user_id = payload.get('user_id')
            roles = payload.get('roles', [])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': {'code': 'TOKEN_EXPIRED', 'message': 'Token has expired.'}}, status=401), None
        except jwt.InvalidTokenError:
            return JsonResponse({'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid token.'}}, status=401), None

        # Check authorization if not public
        if permissions is not None and isinstance(permissions, dict):
            allowed_roles = permissions.get(method)
            if allowed_roles is not None and len(allowed_roles) > 0:
                has_role = any(role in roles for role in allowed_roles)
                if not has_role:
                    return JsonResponse({'error': {'code': 'FORBIDDEN', 'message': 'You do not have permission to access this resource.'}}, status=403), None

        return str(user_id) if user_id else None, ','.join(roles)

    def _proxy_request(self, request, service_name, path):
        port = SERVICE_PORTS.get(service_name)
        if not port:
            return JsonResponse({'error': 'Service not found'}, status=404)

        # 1. Authenticate & Authorize
        auth_result, roles_str = self._authenticate_and_authorize(request, service_name, request.method)
        if isinstance(auth_result, JsonResponse):
            return auth_result # Return error response
        
        user_id = auth_result

        # Construct target URL
        import os
        is_docker = os.environ.get('RUNNING_IN_DOCKER', 'True').lower() in ('true', '1')
        
        if is_docker:
            host = SERVICE_DOCKER_HOSTS.get(service_name)
            target_port = 8000
        else:
            host = '127.0.0.1'
            target_port = port
            
        if path:
            target_url = f'http://{host}:{target_port}/api/v1/{service_name}/{path}'
        else:
            target_url = f'http://{host}:{target_port}/api/v1/{service_name}'
        
        # Prepare headers (forward authorization)
        headers = {key: value for (key, value) in request.headers.items() if key.lower() not in ['host', 'content-length']}
        
        # Add custom headers for downstream services
        if user_id:
            headers['X-User-Id'] = user_id
        if roles_str:
            headers['X-User-Roles'] = roles_str
            
        # Fix for Django DisallowedHost error caused by underscores in Docker service names
        headers['Host'] = 'localhost'
            
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
