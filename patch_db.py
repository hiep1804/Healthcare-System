import os

SERVICES = [
    'api_gateway',
    'identity_service',
    'patient_service',
    'provider_service',
    'appointment_service',
    'consultation_service',
    'medical_record_service',
    'notification_service',
    'audit_service',
    'subscription_service',
    'insurance_service'
]

BASE_DIR = r"e:\TTTN"

DB_CONFIG = """
# PostgreSQL Configuration (overriding SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'healthcare_db'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
"""

def patch_settings():
    for svc in SERVICES:
        settings_path = os.path.join(BASE_DIR, svc, 'config', 'settings.py')
        if not os.path.exists(settings_path):
            print(f"Skipping {settings_path} (not found)")
            continue
            
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Very simple replacement: comment out sqlite config and add postgres
        # In this project, `DATABASES = {}` or `DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3' ... } }`
        
        # To avoid multiple appending, check if postgres is already there
        if "'ENGINE': 'django.db.backends.postgresql'" in content:
            print(f"Already patched {settings_path}")
            continue
            
        # find DATABASES block
        import re
        content = re.sub(r'DATABASES\s*=\s*\{.*?\}', DB_CONFIG.strip(), content, flags=re.DOTALL)
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Patched {settings_path}")

def patch_requirements():
    for svc in SERVICES:
        req_path = os.path.join(BASE_DIR, svc, 'requirements.txt')
        if not os.path.exists(req_path):
            continue
            
        with open(req_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'psycopg2-binary' not in content:
            with open(req_path, 'a', encoding='utf-8') as f:
                f.write("\npsycopg2-binary>=2.9.9\n")
            print(f"Patched {req_path}")
        else:
            print(f"Already patched {req_path}")

if __name__ == '__main__':
    patch_settings()
    patch_requirements()
