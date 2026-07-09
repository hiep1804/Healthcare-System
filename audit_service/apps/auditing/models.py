import uuid
from django.db import models


class AuditLog(models.Model):
    """General logs for system operations."""
    ROLE_CHOICES = [
        ('PATIENT', 'Bệnh nhân'),
        ('DOCTOR', 'Bác sĩ'),
        ('ADMIN', 'Admin Marketplace'),
        ('PROVIDER_ADMIN', 'Provider Admin'),
        ('SYSTEM', 'Hệ thống'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor_user_id = models.UUIDField()
    actor_role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    action = models.CharField(max_length=150, help_text="e.g. VIEW_MEDICAL_RECORD, UPDATE_PASSWORD")
    resource_type = models.CharField(max_length=100, help_text="e.g. PATIENT_RECORD, APPOINTMENT")
    resource_id = models.CharField(max_length=100, blank=True)
    result = models.CharField(max_length=20, choices=[('SUCCESS', 'Thành công'), ('FAILED', 'Thất bại')], default='SUCCESS')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.actor_role}:{self.actor_user_id} -> {self.action} ({self.result})"


class AccessLog(models.Model):
    """Access history logs specifically for patient medical records."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    accessed_by_user_id = models.UUIDField()
    accessed_by_role = models.CharField(max_length=30)
    action = models.CharField(max_length=150, default='VIEW_MEDICAL_RECORD')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'access_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.accessed_by_user_id} accessed patient {self.patient_id} record"


class SecurityEvent(models.Model):
    """Intrusion or security compromise indicators."""
    SEVERITY_CHOICES = [
        ('LOW', 'Thấp'),
        ('MEDIUM', 'Trung bình'),
        ('HIGH', 'Cao'),
        ('CRITICAL', 'Nguy hiểm'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=100, help_text="e.g. MFA_FAILED, BRUTE_FORCE")
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MEDIUM')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'security_events'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} [{self.severity}]"
