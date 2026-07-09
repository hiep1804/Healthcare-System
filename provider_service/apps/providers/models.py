import uuid
from django.db import models


class Specialty(models.Model):
    """Specialties like Cardiology, Pediatrics, etc."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'specialties'
        ordering = ['name']

    def __str__(self):
        return self.name


class Clinic(models.Model):
    """Clinics/Hospitals where doctors practice."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=250)
    address = models.TextField()
    contact_number = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clinics'
        ordering = ['name']

    def __str__(self):
        return self.name


class Provider(models.Model):
    """Doctor/Provider profile linked to identity_service User."""
    STATUS_CHOICES = [
        ('PENDING_VERIFICATION', 'Chờ xác minh'),
        ('VERIFIED', 'Đã xác minh'),
        ('REJECTED', 'Bị từ chối'),
        ('NEED_MORE_INFO', 'Cần thêm thông tin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True, help_text="User ID from identity-service")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=150, blank=True, help_text="City/Region")
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True, blank=True, related_name='providers')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING_VERIFICATION')
    verification_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'providers'
        ordering = ['-created_at']

    def __str__(self):
        return f"Dr. {self.first_name} {self.last_name}"


class DoctorLicense(models.Model):
    """Licenses and certificates uploaded by doctors."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='licenses')
    license_number = models.CharField(max_length=100)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    document_url = models.CharField(max_length=500)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'doctor_licenses'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.license_number} - {self.provider}"


class ProviderService(models.Model):
    """Services and consultation types offered by a doctor."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='services')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='provider_services')
    service_name = models.CharField(max_length=200, help_text="e.g. Online Consultation, Clinic Visit")
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="VND")
    duration_minutes = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'provider_services'
        unique_together = ('provider', 'specialty', 'service_name')

    def __str__(self):
        return f"{self.service_name} - Dr. {self.provider.last_name}"
