import os

DOCKERFILE_CONTENT = """FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
"""

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

def main():
    base_dir = r"e:\TTTN"
    for service in SERVICES:
        path = os.path.join(base_dir, service, "Dockerfile")
        with open(path, "w") as f:
            f.write(DOCKERFILE_CONTENT)
        print(f"Created {path}")

if __name__ == "__main__":
    main()
