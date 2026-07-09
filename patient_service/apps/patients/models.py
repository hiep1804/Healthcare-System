import uuid
from django.db import models


class Patient(models.Model):
    """Patient profile linked to identity-service user by user_id."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True, help_text='User ID from identity-service')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=[('MALE', 'Nam'), ('FEMALE', 'Nữ'), ('OTHER', 'Khác')],
        blank=True,
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    national_id = models.CharField(max_length=20, blank=True, help_text='CCCD/CMND')
    insurance_number = models.CharField(max_length=50, blank=True)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    blood_type = models.CharField(
        max_length=5, blank=True,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Allergy(models.Model):
    """Patient allergies."""
    SEVERITY_CHOICES = [
        ('LOW', 'Thấp'),
        ('MEDIUM', 'Trung bình'),
        ('HIGH', 'Cao'),
        ('CRITICAL', 'Nguy hiểm'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField(max_length=200)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='MEDIUM')
    reaction = models.TextField(blank=True)
    note = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'allergies'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.allergen} ({self.severity})"


class MedicalCondition(models.Model):
    """Patient medical conditions / underlying diseases."""
    STATUS_CHOICES = [
        ('ACTIVE', 'Đang điều trị'),
        ('RESOLVED', 'Đã khỏi'),
        ('CHRONIC', 'Mãn tính'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='conditions')
    condition_name = models.CharField(max_length=300)
    icd_code = models.CharField(max_length=20, blank=True, help_text='ICD-10 code')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    diagnosed_date = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medical_conditions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.condition_name} ({self.status})"


class CurrentMedication(models.Model):
    """Medications the patient is currently taking."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medications')
    drug_name = models.CharField(max_length=300)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    prescribed_by = models.CharField(max_length=200, blank=True)
    note = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'current_medications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.drug_name} - {self.dosage}"


class Consent(models.Model):
    """Patient data sharing consent."""
    CONSENT_TYPES = [
        ('DATA_SHARING', 'Chia sẻ dữ liệu'),
        ('AI_ANALYSIS', 'Phân tích AI'),
        ('RESEARCH', 'Nghiên cứu'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consents')
    consent_type = models.CharField(max_length=30, choices=CONSENT_TYPES)
    granted_to_user_id = models.UUIDField(null=True, blank=True, help_text='Specific user granted access')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    granted_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'consents'
        ordering = ['-granted_at']

    def __str__(self):
        return f"{self.patient} - {self.consent_type}"
