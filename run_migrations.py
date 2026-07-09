import subprocess
import os

SERVICES = [
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

BASE_DIR = r'e:\TTTN'

def run_cmd(service, args):
    cwd = os.path.join(BASE_DIR, service)
    print(f"\n--- Running command in {service}: {' '.join(args)} ---")
    try:
        res = subprocess.run(
            [r'python', 'manage.py'] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        print(res.stdout)
        if res.stderr:
            print("Stderr:", res.stderr)
    except subprocess.CalledProcessError as e:
        print(f"FAILED in {service}:")
        print("Stdout:", e.stdout)
        print("Stderr:", e.stderr)
        raise e

if __name__ == '__main__':
    for service in SERVICES:
        # Check if the app has a models.py file
        # The app name in identity_service is apps.authentication
        # Let's run makemigrations first
        # In Django, makemigrations with the specific app name can create migrations files
        # Let's run plain makemigrations first, then migrate.
        try:
            run_cmd(service, ['makemigrations'])
            run_cmd(service, ['migrate'])
        except Exception as e:
            print(f"Skipping or failed: {e}")
