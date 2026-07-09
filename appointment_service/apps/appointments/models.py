import uuid
from django.db import models


class ProviderSchedule(models.Model):
    """Doctor schedule templates per day of week."""
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider_id = models.UUIDField(help_text="Doctor/Provider ID from provider-service")
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'provider_schedules'
        unique_together = ('provider_id', 'day_of_week', 'start_time', 'end_time')

    def __str__(self):
        return f"Schedule {self.provider_id} - Day {self.day_of_week} ({self.start_time}-{self.end_time})"


class TimeSlot(models.Model):
    """Specific dates and times generated from schedules."""
    STATUS_CHOICES = [
        ('FREE', 'Trống'),
        ('HELD', 'Đang giữ tạm'),
        ('BOOKED', 'Đã đặt'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider_id = models.UUIDField()
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='FREE')
    hold_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'time_slots'
        ordering = ['date', 'start_time']
        unique_together = ('provider_id', 'date', 'start_time', 'end_time')

    def __str__(self):
        return f"Slot {self.date} {self.start_time}-{self.end_time} ({self.status})"


class Appointment(models.Model):
    """Appointment bookings."""
    STATUS_CHOICES = [
        ('DRAFT', 'Lịch nháp'),
        ('HELD', 'Slot đang được giữ tạm'),
        ('PAYMENT_PENDING', 'Chờ thanh toán'),
        ('CONFIRMED', 'Đã xác nhận'),
        ('CANCELLED', 'Đã hủy'),
        ('COMPLETED', 'Đã hoàn tất khám'),
        ('NO_SHOW', 'Không tham gia'),
        ('REFUND_PENDING', 'Đang xử lý hoàn tiền'),
        ('REFUNDED', 'Đã hoàn tiền'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField(help_text="Patient ID from patient-service")
    provider_id = models.UUIDField(help_text="Doctor/Provider ID from provider-service")
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE, related_name='appointment')
    service_id = models.UUIDField(help_text="Service ID from provider-service")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='HELD')
    hold_expires_at = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='VND')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Appt {self.id} - {self.status}"


class AppointmentStatusHistory(models.Model):
    """Audit log of appointment state changes."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=30, choices=Appointment.STATUS_CHOICES)
    notes = models.TextField(blank=True)
    changed_by = models.UUIDField(null=True, blank=True, help_text="User ID who made change")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'appointment_status_history'
        ordering = ['created_at']

    def __str__(self):
        return f"History {self.appointment.id} -> {self.status}"
