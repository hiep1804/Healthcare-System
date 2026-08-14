import subprocess
import time

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
    'insurance_service',
    'ai_cds_service'
]

def run():
    print("Waiting for db to be ready...")
    time.sleep(5)
    
    for svc in SERVICES:
        print(f"Running makemigrations on {svc}...")
        subprocess.run(["docker-compose", "exec", svc, "python", "manage.py", "makemigrations"])
        print(f"Running migrate on {svc}...")
        subprocess.run(["docker-compose", "exec", svc, "python", "manage.py", "migrate"])
        
    print("Running seed_data.py on identity_service...")
    subprocess.run(["docker-compose", "exec", "identity_service", "python", "seed_data.py"])
    
if __name__ == '__main__':
    run()
