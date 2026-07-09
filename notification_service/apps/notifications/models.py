import uuid
from django.db import models


class NotificationTemplate(models.Model):
    """Templates for different communication channels."""
    CHANNEL_CHOICES = [
        ('SMS', 'Tin nhắn SMS'),
        ('EMAIL', 'Thư điện tử'),
        ('PUSH', 'Thông báo ứng dụng'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True, help_text="e.g. APPOINTMENT_CONFIRMED")
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    subject_template = models.CharField(max_length=250, blank=True, help_text="Subject template (mainly for email)")
    body_template = models.TextField(help_text="Body content with variables like {{patient_name}}")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_templates'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} ({self.channel})"


class NotificationJob(models.Model):
    """Queued and processed notification records."""
    STATUS_CHOICES = [
        ('PENDING', 'Đang chờ gửi'),
        ('SENT', 'Đã gửi'),
        ('FAILED', 'Thất bại'),
        ('RETRYING', 'Đang thử lại'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(NotificationTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    recipient_user_id = models.UUIDField()
    channel = models.CharField(max_length=20, choices=NotificationTemplate.CHANNEL_CHOICES)
    recipient_address = models.CharField(max_length=250, help_text="Email address or phone number")
    variables = models.JSONField(default=dict, blank=True, help_text="Key-value variables to render template")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification_jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Job {self.id} -> {self.recipient_address} ({self.status})"


class DeliveryLog(models.Model):
    """Logs from delivery partners (Twilio, Sendgrid, etc.)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(NotificationJob, on_delete=models.CASCADE, related_name='delivery_logs')
    status = models.CharField(max_length=50)
    response_payload = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'delivery_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Log {self.id} for Job {self.job_id}"
