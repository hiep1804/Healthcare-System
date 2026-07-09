from django.contrib import admin
from .models import NotificationTemplate, NotificationJob, DeliveryLog


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('code', 'channel', 'subject_template', 'created_at')
    list_filter = ('channel',)
    search_fields = ('code', 'subject_template')


@admin.register(NotificationJob)
class NotificationJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient_address', 'channel', 'status', 'sent_at', 'created_at')
    list_filter = ('channel', 'status')
    search_fields = ('recipient_address', 'recipient_user_id')


@admin.register(DeliveryLog)
class DeliveryLogAdmin(admin.ModelAdmin):
    list_display = ('job', 'status', 'created_at')
    list_filter = ('status',)
