"""
Script to generate boilerplate common files for remaining services.
This creates the common/ directory files and config files that are identical
across all non-identity services.
"""
import os
import sys

SERVICES = [
    ('provider_service', 'provider_db', 'apps.providers', 'Providers'),
    ('appointment_service', 'appointment_db', 'apps.appointments', 'Appointments'),
    ('consultation_service', 'consultation_db', 'apps.consultations', 'Consultations'),
    ('medical_record_service', 'medical_record_db', 'apps.records', 'Medical Records'),
    ('notification_service', 'notification_db', 'apps.notifications', 'Notifications'),
    ('audit_service', 'audit_db', 'apps.auditing', 'Auditing'),
    ('subscription_service', 'subscription_db', 'apps.subscriptions', 'Subscriptions'),
    ('insurance_service', 'insurance_db', 'apps.insurance', 'Insurance'),
]

BASE_DIR = r'e:\TTTN'

MANAGE_PY = '''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
'''

REQUIREMENTS = '''Django>=5.0,<6.0
djangorestframework>=3.14,<4.0
djangorestframework-simplejwt>=5.3,<6.0
django-cors-headers>=4.3,<5.0
PyJWT>=2.8,<3.0
'''

MIDDLEWARE = '''import uuid
from django.utils.deprecation import MiddlewareMixin


class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request_id = request.META.get('HTTP_X_REQUEST_ID', str(uuid.uuid4()))
        correlation_id = request.META.get('HTTP_X_CORRELATION_ID', request_id)
        request.request_id = request_id
        request.correlation_id = correlation_id

    def process_response(self, request, response):
        request_id = getattr(request, 'request_id', None)
        correlation_id = getattr(request, 'correlation_id', None)
        if request_id:
            response['X-Request-Id'] = request_id
        if correlation_id:
            response['X-Correlation-Id'] = correlation_id
        return response
'''

EXCEPTIONS = '''from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    request = context.get('request')
    request_id = getattr(request, 'request_id', None) if request else None

    if response is not None:
        error_code = getattr(exc, 'default_code', 'ERROR')
        if isinstance(error_code, str):
            error_code = error_code.upper()
        else:
            error_code = 'ERROR'
        message = str(exc.detail) if hasattr(exc, 'detail') else str(exc)
        error_response = {
            'error': {
                'code': error_code,
                'message': message,
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data},
                'request_id': request_id,
            }
        }
        response.data = error_response
        return response

    return Response(
        {'error': {'code': 'INTERNAL_SERVER_ERROR', 'message': 'An unexpected error occurred.', 'details': {}, 'request_id': request_id}},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
'''

PAGINATION = '''from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('data', data),
            ('pagination', OrderedDict([
                ('page', self.page.number),
                ('page_size', self.get_page_size(self.request)),
                ('total', self.page.paginator.count),
            ])),
        ]))
'''

AUTHENTICATION = '''import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTUser:
    def __init__(self, payload):
        self.id = payload.get('user_id')
        self.payload = payload
        self.is_authenticated = True
        self.roles = payload.get('roles', [])

    def __str__(self):
        return f"JWTUser({self.id})"

    def has_role(self, role_name):
        return role_name in self.roles


class JWTServiceAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": True},
            )
            user = JWTUser(payload)
            return (user, token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')
'''

PERMISSIONS = '''from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'has_role') and request.user.has_role('ADMIN')


class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'has_role') and request.user.has_role('DOCTOR')


class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'has_role') and request.user.has_role('PATIENT')


class IsProviderAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'has_role') and request.user.has_role('PROVIDER_ADMIN')


class IsDoctorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'has_role'):
            return False
        return request.user.has_role('DOCTOR') or request.user.has_role('ADMIN')


class IsPatientOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'has_role'):
            return False
        return request.user.has_role('PATIENT') or request.user.has_role('ADMIN')


class IsPatientOrDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'has_role'):
            return False
        return request.user.has_role('PATIENT') or request.user.has_role('DOCTOR')


class IsPatientOrDoctorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'has_role'):
            return False
        return (request.user.has_role('PATIENT') or request.user.has_role('DOCTOR') or request.user.has_role('ADMIN'))
'''

WSGI_TEMPLATE = '''import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
'''

def get_settings(service_name, db_name, app_name, app_label):
    return f'''import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-{service_name}-dev-key-change-in-production'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    '{app_name}',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'common.middleware.RequestIDMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / '{db_name}.sqlite3',
    }}
}}

LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = DEBUG

REST_FRAMEWORK = {{
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'common.authentication.JWTServiceAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',
}}

JWT_SECRET_KEY = os.environ.get(
    'JWT_SECRET_KEY',
    'django-insecure-identity-service-dev-key-change-in-production'
)
JWT_ALGORITHM = 'HS256'
'''

def get_urls(app_name):
    return f'''from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('{app_name}.urls')),
]
'''

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  Created: {path}')

def generate_service(service_name, db_name, app_name, app_label):
    service_dir = os.path.join(BASE_DIR, service_name)
    app_parts = app_name.split('.')
    app_dir = os.path.join(service_dir, *app_parts)

    print(f'\nGenerating {service_name}...')

    # Root files
    write_file(os.path.join(service_dir, 'manage.py'), MANAGE_PY)
    write_file(os.path.join(service_dir, 'requirements.txt'), REQUIREMENTS)

    # Config
    write_file(os.path.join(service_dir, 'config', '__init__.py'), '# config\n')
    write_file(os.path.join(service_dir, 'config', 'settings.py'), get_settings(service_name, db_name, app_name, app_label))
    write_file(os.path.join(service_dir, 'config', 'urls.py'), get_urls(app_name))
    write_file(os.path.join(service_dir, 'config', 'wsgi.py'), WSGI_TEMPLATE)

    # Common
    write_file(os.path.join(service_dir, 'common', '__init__.py'), '# common\n')
    write_file(os.path.join(service_dir, 'common', 'middleware.py'), MIDDLEWARE)
    write_file(os.path.join(service_dir, 'common', 'exceptions.py'), EXCEPTIONS)
    write_file(os.path.join(service_dir, 'common', 'pagination.py'), PAGINATION)
    write_file(os.path.join(service_dir, 'common', 'authentication.py'), AUTHENTICATION)
    write_file(os.path.join(service_dir, 'common', 'permissions.py'), PERMISSIONS)

    # App package inits
    write_file(os.path.join(service_dir, 'apps', '__init__.py'), '# apps\n')
    write_file(os.path.join(app_dir, '__init__.py'), f'# {app_label}\n')

    # App config
    app_class = app_parts[-1].capitalize() + 'Config'
    write_file(os.path.join(app_dir, 'apps.py'), f'''from django.apps import AppConfig


class {app_class}(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
    verbose_name = '{app_label}'
''')

    print(f'  Done generating boilerplate for {service_name}')


if __name__ == '__main__':
    for service in SERVICES:
        generate_service(*service)
    print('\nAll boilerplate generated successfully!')
