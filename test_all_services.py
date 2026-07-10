"""
Script kiểm tra tất cả 10 microservices có khởi động và phản hồi được không.
Cách dùng: python test_all_services.py
"""
import subprocess
import time
import sys
import json
import urllib.request
import urllib.error
import os
import signal

BASE_DIR = r'e:\TTTN'

SERVICES = [
    {'name': 'api-gateway',            'dir': 'api_gateway',            'port': 8000, 'test_url': '/api/v1/auth/register'},
    {'name': 'patient-service',        'dir': 'patient_service',        'port': 8002, 'test_url': '/api/v1/patients'},
    {'name': 'provider-service',       'dir': 'provider_service',       'port': 8003, 'test_url': '/api/v1/specialties'},
    {'name': 'appointment-service',    'dir': 'appointment_service',    'port': 8004, 'test_url': '/api/v1/appointments'},
    {'name': 'consultation-service',   'dir': 'consultation_service',   'port': 8005, 'test_url': '/api/v1/consultations'},
    {'name': 'medical-record-service', 'dir': 'medical_record_service', 'port': 8006, 'test_url': '/api/v1/patients/00000000-0000-0000-0000-000000000000/records'},
    {'name': 'notification-service',   'dir': 'notification_service',   'port': 8007, 'test_url': '/api/v1/notification-templates'},
    {'name': 'audit-service',          'dir': 'audit_service',          'port': 8008, 'test_url': '/api/v1/audit/events'},
    {'name': 'subscription-service',   'dir': 'subscription_service',   'port': 8009, 'test_url': '/api/v1/plans'},
    {'name': 'insurance-service',      'dir': 'insurance_service',      'port': 8010, 'test_url': '/api/v1/insurance-policies'},
]


def start_service(service):
    """Khởi động service và trả về process handle."""
    cwd = os.path.join(BASE_DIR, service['dir'])
    proc = subprocess.Popen(
        [sys.executable, 'manage.py', 'runserver', str(service['port']), '--noreload'],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0,
    )
    return proc


def check_health(service, retries=5, delay=1.5):
    """Kiểm tra xem service có phản hồi HTTP hay không."""
    url = f"http://127.0.0.1:{service['port']}{service['test_url']}"
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, method='GET')
            resp = urllib.request.urlopen(req, timeout=3)
            return resp.status, 'OK'
        except urllib.error.HTTPError as e:
            # 401/403 nghĩa là service đang chạy nhưng cần auth -> OK
            if e.code in (401, 403, 405):
                return e.code, 'OK (auth required - service is running)'
            return e.code, f'HTTP Error: {e.code}'
        except urllib.error.URLError:
            time.sleep(delay)
        except Exception as e:
            time.sleep(delay)
    return 0, 'FAILED - Service không phản hồi sau nhiều lần thử'


def stop_service(proc):
    """Dừng service process."""
    try:
        if os.name == 'nt':
            proc.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            proc.terminate()
        proc.wait(timeout=5)
    except Exception:
        proc.kill()


def main():
    print("=" * 70)
    print("  KIỂM TRA TẤT CẢ MICROSERVICES - Healthcare Marketplace")
    print("=" * 70)
    print()

    processes = []
    results = []

    # Bước 1: Khởi động tất cả services
    print("[1/3] Khởi động tất cả services...")
    for svc in SERVICES:
        print(f"  🚀 Starting {svc['name']} on port {svc['port']}...", end=' ')
        proc = start_service(svc)
        processes.append((svc, proc))
        print("started (PID: {})".format(proc.pid))

    # Chờ cho các server khởi động xong
    print(f"\n[2/3] Chờ 5 giây để tất cả services khởi động...")
    time.sleep(5)

    # Bước 2: Kiểm tra health check
    print("\n[3/3] Kiểm tra phản hồi từ các services...\n")
    print(f"  {'Service':<30} {'Port':<8} {'Status':<8} {'Kết quả'}")
    print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*35}")

    all_ok = True
    for svc, proc in processes:
        status_code, message = check_health(svc)
        is_ok = status_code != 0
        status_icon = "✅" if is_ok else "❌"
        results.append({
            'name': svc['name'],
            'port': svc['port'],
            'ok': is_ok,
            'status': status_code,
            'message': message,
        })
        if not is_ok:
            all_ok = False
        print(f"  {status_icon} {svc['name']:<28} {svc['port']:<8} {status_code:<8} {message}")

    # Bước 3: Dừng tất cả services
    print("\n" + "=" * 70)
    print("  Dừng tất cả services...")
    for svc, proc in processes:
        stop_service(proc)
        print(f"  ⏹  Stopped {svc['name']} (PID: {proc.pid})")

    # Tổng kết
    print("\n" + "=" * 70)
    ok_count = sum(1 for r in results if r['ok'])
    total = len(results)
    if all_ok:
        print(f"  🎉 KẾT QUẢ: TẤT CẢ {total}/{total} SERVICES CHẠY THÀNH CÔNG!")
    else:
        print(f"  ⚠️  KẾT QUẢ: {ok_count}/{total} services chạy được.")
        for r in results:
            if not r['ok']:
                print(f"     ❌ {r['name']}: {r['message']}")
    print("=" * 70)

    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
