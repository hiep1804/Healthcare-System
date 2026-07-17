import subprocess
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    {'name': 'API Gateway',            'dir': 'api_gateway',            'cmd': ['cmd.exe', '/k', sys.executable, 'manage.py', 'runserver', '8000']},
    {'name': 'Identity Service',       'dir': 'identity_service',       'cmd': ['cmd.exe', '/k', sys.executable, 'manage.py', 'runserver', '8001']},
    {'name': 'Patient Service',        'dir': 'patient_service',        'cmd': ['cmd.exe', '/k', sys.executable, 'manage.py', 'runserver', '8002']},
    {'name': 'Provider Service',       'dir': 'provider_service',       'cmd': ['cmd.exe', '/k', sys.executable, 'manage.py', 'runserver', '8003']},
    {'name': 'Appointment Service',    'dir': 'appointment_service',    'cmd': ['cmd.exe', '/k', sys.executable, 'manage.py', 'runserver', '8004']},
    {'name': 'Consultation Service',   'dir': 'consultation_service',   'cmd': ['cmd.exe', '/k', sys.executable, 'manage.py', 'runserver', '8005']},
    {'name': 'Medical Record Service', 'dir': 'medical_record_service', 'cmd': ['cmd.exe', '/k', sys.executable, 'manage.py', 'runserver', '8006']},
    {'name': 'Notification Service',   'dir': 'notification_service',   'cmd': ['cmd.exe', '/k', sys.executable, 'manage.py', 'runserver', '8007']},
    {'name': 'Audit Service',          'dir': 'audit_service',          'cmd': ['cmd.exe', '/k', sys.executable, 'manage.py', 'runserver', '8008']},
    {'name': 'Subscription Service',   'dir': 'subscription_service',   'cmd': ['cmd.exe', '/k', sys.executable, 'manage.py', 'runserver', '8009']},
    {'name': 'Insurance Service',      'dir': 'insurance_service',      'cmd': ['cmd.exe', '/k', sys.executable, 'manage.py', 'runserver', '8010']},
    {'name': 'Frontend Portal',        'dir': 'frontend_portal',        'cmd': ['cmd.exe', '/k', 'npm', 'run', 'dev', '--', '--port', '5173']},
]

def main():
    print("=" * 60)
    print("🚀 STARTING HEALTHCARE MICROSERVICES SYSTEM 🚀")
    print("=" * 60)
    
    processes = []
    
    # 0x00000010 is CREATE_NEW_CONSOLE in Windows
    CREATE_NEW_CONSOLE = 0x00000010
    
    for svc in SERVICES:
        cwd = os.path.join(BASE_DIR, svc['dir'])
        print(f"Starting {svc['name']} in a new window...")
        
        try:
            # Mở mỗi service trong một cửa sổ CMD/Terminal mới
            p = subprocess.Popen(
                svc['cmd'], 
                cwd=cwd, 
                creationflags=CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            processes.append(p)
        except Exception as e:
            print(f"❌ Failed to start {svc['name']}: {e}")

    print("=" * 60)
    print("✅ All services have been launched in separate windows!")
    print("👉 Access the system at: http://localhost:5173")
    print("⚠️  To stop the system, simply close the opened command windows.")
    print("=" * 60)

if __name__ == '__main__':
    main()
