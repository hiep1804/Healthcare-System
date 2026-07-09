from django.contrib import admin
from .models import AuditLog, AccessLog, SecurityEvent


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('actor_role', 'actor_user_id', 'action', 'resource_type', 'result', 'created_at')
    list_filter = ('actor_role', 'result')
    search_fields = ('action', 'actor_user_id')


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'accessed_by_user_id', 'accessed_by_role', 'action', 'created_at')
    list_filter = ('accessed_by_role',)
    search_fields = ('patient_id', 'accessed_by_user_id')


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'severity', 'ip_address', 'created_at')
    list_filter = ('severity',)
    search_fields = ('event_type', 'description')
