from django.contrib import admin
from .models import Consultation, ClinicalNote, Diagnosis, Prescription, PrescriptionItem, AIDecision


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'appointment_id', 'patient_id', 'provider_id', 'status', 'start_time')
    list_filter = ('status',)
    search_fields = ('patient_id', 'provider_id')


@admin.register(ClinicalNote)
class ClinicalNoteAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'created_at', 'updated_at')


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'diagnosis_text', 'icd_code', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('diagnosis_text', 'icd_code')


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'issued_at')


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ('prescription', 'drug_name', 'dosage', 'frequency', 'quantity')


@admin.register(AIDecision)
class AIDecisionAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'recommendation_id', 'action', 'created_at')
    list_filter = ('action',)
