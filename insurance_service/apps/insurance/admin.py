from django.contrib import admin
from .models import InsurancePolicy, EligibilityCheck, Claim, ClaimItem


@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'patient_id', 'provider_name', 'expiry_date', 'status')
    list_filter = ('status', 'provider_name')
    search_fields = ('policy_number', 'patient_id')


@admin.register(EligibilityCheck)
class EligibilityCheckAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'policy', 'provider_id', 'status', 'check_date')
    list_filter = ('status',)


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'appointment_id', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('patient_id', 'appointment_id')


@admin.register(ClaimItem)
class ClaimItemAdmin(admin.ModelAdmin):
    list_display = ('claim', 'description', 'amount')
