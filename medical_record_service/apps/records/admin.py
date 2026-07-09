from django.contrib import admin
from .models import MedicalRecord, MedicalDocument, LabResult, LabResultItem, Vitals


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient_id', 'record_type', 'created_by', 'created_at')
    list_filter = ('record_type', 'created_at')
    search_fields = ('title', 'patient_id')


@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'patient_id', 'document_type', 'is_parsed', 'uploaded_by')
    list_filter = ('document_type', 'is_parsed')
    search_fields = ('file_name', 'patient_id')


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'test_date', 'laboratory_name')
    list_filter = ('test_date',)
    search_fields = ('patient_id', 'laboratory_name')


@admin.register(LabResultItem)
class LabResultItemAdmin(admin.ModelAdmin):
    list_display = ('lab_result', 'test_name', 'value', 'unit', 'status')
    list_filter = ('status',)
    search_fields = ('test_name',)


@admin.register(Vitals)
class VitalsAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'blood_pressure_systolic', 'blood_pressure_diastolic', 'heart_rate', 'temperature_c', 'recorded_at')
    list_filter = ('recorded_at',)
    search_fields = ('patient_id',)
