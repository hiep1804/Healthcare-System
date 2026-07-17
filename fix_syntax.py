import os
import re

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

def fix():
    for svc in SERVICES:
        settings_path = os.path.join(BASE_DIR, svc, 'config', 'settings.py')
        if not os.path.exists(settings_path):
            continue
            
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Replace the double closing braces left by my regex mistake
        content = content.replace("    }\n}\n}", "    }\n}")
        
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {settings_path}")

if __name__ == '__main__':
    fix()
