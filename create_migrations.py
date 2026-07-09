import os
import subprocess

SERVICES_APPS = [
    ('identity_service', 'apps/authentication'),
    ('patient_service', 'apps/patients'),
    ('provider_service', 'apps/providers'),
    ('appointment_service', 'apps/appointments'),
    ('consultation_service', 'apps/consultations'),
    ('medical_record_service', 'apps/records'),
    ('notification_service', 'apps/notifications'),
    ('audit_service', 'apps/auditing'),
    ('subscription_service', 'apps/subscriptions'),
    ('insurance_service', 'apps/insurance')
]

BASE_DIR = r'e:\TTTN'

def init_migrations():
    for service, app_path in SERVICES_APPS:
        migrations_dir = os.path.join(BASE_DIR, service, app_path, 'migrations')
        os.makedirs(migrations_dir, exist_ok=True)
        init_file = os.path.join(migrations_dir, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# init\n')
            print(f"Created migrations init for {service}/{app_path}")

        # Now run python manage.py makemigrations
        cwd = os.path.join(BASE_DIR, service)
        print(f"\n--- Running makemigrations in {service} ---")
        subprocess.run(['python', 'manage.py', 'makemigrations'], cwd=cwd)

        print(f"--- Running migrate in {service} ---")
        subprocess.run(['python', 'manage.py', 'migrate'], cwd=cwd)

if __name__ == '__main__':
    init_migrations()
