"""
Script to add Swagger UI (drf-spectacular) to all 10 microservices.
Updates settings.py and urls.py for each service.
"""
import os
import re

BASE_DIR = r'e:\TTTN'

SERVICES = [
    {'dir': 'identity_service',       'title': 'Identity Service',       'desc': 'Authentication, Users, Roles, MFA'},
    {'dir': 'patient_service',        'title': 'Patient Service',        'desc': 'Patient profiles, Allergies, Conditions, Medications, Consents'},
    {'dir': 'provider_service',       'title': 'Provider Service',       'desc': 'Doctors, Clinics, Specialties, Licenses, Services'},
    {'dir': 'appointment_service',    'title': 'Appointment Service',    'desc': 'Schedules, Slots, Bookings, Hold/Confirm/Cancel'},
    {'dir': 'consultation_service',   'title': 'Consultation Service',   'desc': 'Clinical Notes (SOAP), Diagnoses, Prescriptions, AI Decisions'},
    {'dir': 'medical_record_service', 'title': 'Medical Record Service', 'desc': 'Health Records, Documents, Lab Results, Vitals'},
    {'dir': 'notification_service',   'title': 'Notification Service',   'desc': 'Templates, SMS/Email/Push, Delivery Logs'},
    {'dir': 'audit_service',          'title': 'Audit Service',          'desc': 'Audit Logs, Access Logs, Security Events'},
    {'dir': 'subscription_service',   'title': 'Subscription Service',   'desc': 'Plans, Entitlements, Subscriptions, Usage'},
    {'dir': 'insurance_service',      'title': 'Insurance Service',      'desc': 'Policies, Eligibility Checks, Claims'},
]


def update_settings(service):
    settings_path = os.path.join(BASE_DIR, service['dir'], 'config', 'settings.py')
    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already added
    if 'drf_spectacular' in content:
        print(f"  [SKIP] {service['dir']}/config/settings.py already has drf_spectacular")
        return

    # Add drf_spectacular to INSTALLED_APPS
    content = content.replace(
        "    'rest_framework',",
        "    'rest_framework',\n    'drf_spectacular',"
    )

    # Add SPECTACULAR_SETTINGS
    spectacular_config = f"""

# drf-spectacular (Swagger UI)
SPECTACULAR_SETTINGS = {{
    'TITLE': '{service["title"]} API',
    'DESCRIPTION': '{service["desc"]}',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {{
        'deepLinking': True,
        'persistAuthorization': True,
        'displayRequestDuration': True,
    }},
    'COMPONENT_SPLIT_REQUEST': True,
}}
"""
    content += spectacular_config

    # Update DEFAULT_SCHEMA_CLASS in REST_FRAMEWORK
    if "'DEFAULT_SCHEMA_CLASS'" not in content:
        content = content.replace(
            "'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',",
            "'EXCEPTION_HANDLER': 'common.exceptions.custom_exception_handler',\n    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',"
        )

    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  [OK] Updated {service['dir']}/config/settings.py")


def update_urls(service):
    urls_path = os.path.join(BASE_DIR, service['dir'], 'config', 'urls.py')
    with open(urls_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'SpectacularSwaggerView' in content:
        print(f"  [SKIP] {service['dir']}/config/urls.py already has Swagger URLs")
        return

    new_content = """from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
"""

    # Find the app include line
    app_include = None
    for line in content.split('\n'):
        if "include(" in line and "api/v1" in line:
            app_include = line.strip().rstrip(',')
            break

    if app_include:
        new_content += f"    {app_include},\n"
    else:
        # fallback: try to find any include line
        for line in content.split('\n'):
            if "include(" in line:
                app_include = line.strip().rstrip(',')
                new_content += f"    {app_include},\n"
                break

    new_content += """
    # Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Root redirect to Swagger
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='root'),
]
"""

    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"  [OK] Updated {service['dir']}/config/urls.py")


if __name__ == '__main__':
    print("Adding Swagger UI to all microservices...\n")
    for svc in SERVICES:
        print(f"\n--- {svc['title']} ({svc['dir']}) ---")
        update_settings(svc)
        update_urls(svc)
    print("\n\nDone! Access Swagger UI at http://127.0.0.1:<port>/api/docs/")
    print("Or just http://127.0.0.1:<port>/ (redirects to Swagger)")
