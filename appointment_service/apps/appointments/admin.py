from django.contrib import admin
from .models import ProviderSchedule, TimeSlot, Appointment, AppointmentStatusHistory


@admin.register(ProviderSchedule)
class ProviderScheduleAdmin(admin.ModelAdmin):
    list_display = ('provider_id', 'day_of_week', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active')
    search_fields = ('provider_id',)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('provider_id', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('provider_id',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'provider_id', 'status', 'amount', 'created_at')
    list_filter = ('status',)
    search_fields = ('patient_id', 'provider_id')


@admin.register(AppointmentStatusHistory)
class AppointmentStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'status', 'changed_by', 'created_at')
    list_filter = ('status',)
