from django.contrib import admin
from .models import Patient, Allergy, MedicalCondition, CurrentMedication, Consent


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'gender', 'phone', 'city', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone')
    list_filter = ('gender', 'city')


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('patient', 'allergen', 'severity', 'is_active', 'created_at')
    list_filter = ('severity', 'is_active')


@admin.register(MedicalCondition)
class MedicalConditionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'condition_name', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(CurrentMedication)
class CurrentMedicationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'drug_name', 'dosage', 'frequency', 'is_active')
    list_filter = ('is_active',)


@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'consent_type', 'is_active', 'granted_at', 'revoked_at')
    list_filter = ('consent_type', 'is_active')
