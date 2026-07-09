import uuid
from django.db import models
from django.utils import timezone



class MedicalRecord(models.Model):
    """General health records and notes."""
    RECORD_TYPES = [
        ('CONSULTATION_NOTE', 'Ghi chú khám'),
        ('EXTERNAL_DOC', 'Tài liệu bên ngoài'),
        ('DISCHARGE_SUMMARY', 'Tóm tắt xuất viện'),
        ('SURGERY_REPORT', 'Báo cáo phẫu thuật'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    record_type = models.CharField(max_length=50, choices=RECORD_TYPES, default='CONSULTATION_NOTE')
    created_by = models.UUIDField(help_text="User ID of doctor/creator")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medical_records'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.record_type}"


class MedicalDocument(models.Model):
    """File attachments, scanned reports, images."""
    DOC_TYPES = [
        ('LAB_RESULT', 'Kết quả xét nghiệm'),
        ('PRESCRIPTION', 'Đơn thuốc'),
        ('DISCHARGE', 'Giấy xuất viện'),
        ('IMAGING', 'Chẩn đoán hình ảnh'),
        ('OTHER', 'Khác'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    file_name = models.CharField(max_length=250)
    file_type = models.CharField(max_length=100, help_text="e.g. application/pdf, image/jpeg")
    document_type = models.CharField(max_length=50, choices=DOC_TYPES, default='LAB_RESULT')
    storage_url = models.CharField(max_length=500)
    is_parsed = models.BooleanField(default=False)
    uploaded_by = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'medical_documents'
        ordering = ['-created_at']

    def __str__(self):
        return self.file_name


class LabResult(models.Model):
    """Laboratory test reports."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    test_date = models.DateField()
    laboratory_name = models.CharField(max_length=250, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lab_results'
        ordering = ['-test_date', '-created_at']

    def __str__(self):
        return f"Lab on {self.test_date} at {self.laboratory_name or 'N/A'}"


class LabResultItem(models.Model):
    """Specific values within a lab report."""
    STATUS_CHOICES = [
        ('NORMAL', 'Bình thường'),
        ('HIGH', 'Cao'),
        ('LOW', 'Thấp'),
        ('CRITICAL', 'Nguy kịch'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lab_result = models.ForeignKey(LabResult, on_delete=models.CASCADE, related_name='items')
    test_name = models.CharField(max_length=200, help_text="e.g. glucose, HbA1c, RBC")
    value = models.CharField(max_length=50)
    unit = models.CharField(max_length=30, blank=True)
    reference_range = models.CharField(max_length=100, blank=True, help_text="e.g. 70-100 mg/dL")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NORMAL')

    class Meta:
        db_table = 'lab_result_items'

    def __str__(self):
        return f"{self.test_name}: {self.value} {self.unit} ({self.status})"


class Vitals(models.Model):
    """Vital signs records."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    blood_pressure_systolic = models.IntegerField(null=True, blank=True, help_text="mmHg")
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True, help_text="mmHg")
    heart_rate = models.IntegerField(null=True, blank=True, help_text="bpm")
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="Celsius")
    respiratory_rate = models.IntegerField(null=True, blank=True, help_text="breaths/min")
    oxygen_saturation = models.IntegerField(null=True, blank=True, help_text="SpO2 %")
    recorded_by = models.UUIDField()
    recorded_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vitals'
        ordering = ['-created_at']

    def __str__(self):
        return f"Vitals for {self.patient_id} recorded at {self.created_at}"
