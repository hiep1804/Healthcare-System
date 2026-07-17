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

def fix():
    for svc in SERVICES:
        req_path = os.path.join(BASE_DIR, svc, 'requirements.txt')
        if not os.path.exists(req_path):
            continue
            
        with open(req_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'drf-spectacular' not in content:
            with open(req_path, 'a', encoding='utf-8') as f:
                f.write("drf-spectacular>=0.27.1\n")
            print(f"Patched {req_path}")

if __name__ == '__main__':
    fix()
