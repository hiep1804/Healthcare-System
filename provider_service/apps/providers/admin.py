from django.contrib import admin
from .models import Specialty, Clinic, Provider, DoctorLicense, ProviderService


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'contact_number')
    search_fields = ('name', 'address')


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'location', 'rating', 'status', 'created_at')
    list_filter = ('status', 'location')
    search_fields = ('first_name', 'last_name', 'bio')


@admin.register(DoctorLicense)
class DoctorLicenseAdmin(admin.ModelAdmin):
    list_display = ('provider', 'license_number', 'issue_date', 'expiry_date', 'is_verified')
    list_filter = ('is_verified',)
    search_fields = ('license_number', 'provider__first_name', 'provider__last_name')


@admin.register(ProviderService)
class ProviderServiceAdmin(admin.ModelAdmin):
    list_display = ('provider', 'specialty', 'service_name', 'price', 'duration_minutes')
    list_filter = ('specialty',)
    search_fields = ('service_name', 'provider__first_name', 'provider__last_name')
