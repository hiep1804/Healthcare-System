import uuid
from django.db import models


class Consultation(models.Model):
    """Consultation sessions."""
    STATUS_CHOICES = [
        ('DRAFT', 'Lịch nháp'),
        ('IN_PROGRESS', 'Đang thực hiện'),
        ('COMPLETED', 'Đã hoàn tất'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment_id = models.UUIDField(unique=True)
    patient_id = models.UUIDField()
    provider_id = models.UUIDField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'consultations'
        ordering = ['-created_at']

    def __str__(self):
        return f"Consultation {self.id} (Appt: {self.appointment_id})"


class ClinicalNote(models.Model):
    """Clinical notes based on SOAP framework."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='clinical_note')
    subjective = models.TextField(blank=True, help_text="Symptom descriptions, patient history")
    objective = models.TextField(blank=True, help_text="Vitals, physical exams, lab reviews")
    assessment = models.TextField(blank=True, help_text="Differential diagnoses, progression analysis")
    plan = models.TextField(blank=True, help_text="Therapy, follow-ups, diagnostic orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clinical_notes'

    def __str__(self):
        return f"SOAP Note for {self.consultation_id}"


class Diagnosis(models.Model):
    """Diagnoses recorded during the consultation."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='diagnoses')
    diagnosis_text = models.CharField(max_length=300)
    icd_code = models.CharField(max_length=20, blank=True, help_text="ICD-10 code")
    is_primary = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'diagnoses'
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"{self.diagnosis_text} ({self.icd_code})"


class Prescription(models.Model):
    """Prescriptions issued."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='prescription')
    notes = models.TextField(blank=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prescriptions'

    def __str__(self):
        return f"Prescription {self.id}"


class PrescriptionItem(models.Model):
    """Specific medications within a prescription."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    drug_name = models.CharField(max_length=250)
    dosage = models.CharField(max_length=100, help_text="e.g. 500mg, 1 tablet")
    frequency = models.CharField(max_length=100, help_text="e.g. 2 times a day")
    duration_days = models.IntegerField()
    quantity = models.IntegerField()
    instructions = models.TextField(blank=True, help_text="Usage instructions")

    class Meta:
        db_table = 'prescription_items'

    def __str__(self):
        return f"{self.drug_name} x {self.quantity}"


class AIDecision(models.Model):
    """Tracks how doctors interacted with AI recommendations."""
    ACTION_CHOICES = [
        ('ACCEPTED', 'Accepted'),
        ('IGNORED', 'Ignored'),
        ('EDITED', 'Edited'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='ai_decisions')
    recommendation_id = models.CharField(max_length=100)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    doctor_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_decisions'
        ordering = ['-created_at']

    def __str__(self):
        return f"AI Decision on {self.recommendation_id} - {self.action}"
