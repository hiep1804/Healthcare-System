import uuid
from django.db import models


class InsurancePolicy(models.Model):
    """Insurance plans held by patients."""
    STATUS_CHOICES = [
        ('ACTIVE', 'Còn hiệu lực'),
        ('EXPIRED', 'Hết hiệu lực'),
        ('PENDING', 'Chờ xử lý'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    provider_name = models.CharField(max_length=200, help_text="e.g. Bảo Việt, Prudential")
    policy_number = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    co_pay_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="e.g. 20.00 for 20% co-payment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'insurance_policies'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.provider_name} - {self.policy_number}"


class EligibilityCheck(models.Model):
    """Inquiry logs verifying insurance coverage."""
    STATUS_CHOICES = [
        ('ELIGIBLE', 'Đủ điều kiện'),
        ('NOT_ELIGIBLE', 'Không đủ điều kiện'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    policy = models.ForeignKey(InsurancePolicy, on_delete=models.CASCADE, related_name='eligibility_checks')
    provider_id = models.UUIDField(help_text="Doctor/Clinic provider checking eligibility")
    check_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ELIGIBLE')
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'eligibility_checks'
        ordering = ['-check_date']

    def __str__(self):
        return f"Check {self.id} -> {self.status}"


class Claim(models.Model):
    """Claim requests submitted to insurance providers."""
    STATUS_CHOICES = [
        ('SUBMITTED', 'Đã nộp'),
        ('APPROVED', 'Đã phê duyệt'),
        ('REJECTED', 'Bị từ chối'),
        ('PAID', 'Đã chi trả'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    policy = models.ForeignKey(InsurancePolicy, on_delete=models.PROTECT, related_name='claims')
    appointment_id = models.UUIDField(unique=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    claimed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    processed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'claims'
        ordering = ['-created_at']

    def __str__(self):
        return f"Claim {self.id} - Appt: {self.appointment_id} ({self.status})"


class ClaimItem(models.Model):
    """Specific line items within an insurance claim."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=250)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'claim_items'

    def __str__(self):
        return f"{self.description}: {self.amount}"
