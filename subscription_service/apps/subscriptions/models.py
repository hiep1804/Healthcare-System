import uuid
from django.db import models


class Plan(models.Model):
    """Available subscription plans."""
    CYCLE_CHOICES = [
        ('MONTHLY', 'Hàng tháng'),
        ('ANNUALLY', 'Hàng năm'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, unique=True, help_text="e.g. BASIC_MONTHLY, PRO_ANNUAL")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, help_text="Price in VND")
    billing_cycle = models.CharField(max_length=20, choices=CYCLE_CHOICES, default='MONTHLY')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'plans'
        ordering = ['price']

    def __str__(self):
        return f"{self.name} ({self.billing_cycle})"


class PlanEntitlement(models.Model):
    """Features and limits included in a plan."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='entitlements')
    feature_code = models.CharField(max_length=100, help_text="e.g. VISITS_LIMIT, AI_CDS_ACCESS")
    value = models.CharField(max_length=100, help_text="Limit value or Boolean status")
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'plan_entitlements'
        unique_together = ('plan', 'feature_code')

    def __str__(self):
        return f"{self.plan.name} - {self.feature_code}: {self.value}"


class Subscription(models.Model):
    """User subscription records."""
    STATUS_CHOICES = [
        ('ACTIVE', 'Đang hoạt động'),
        ('TRIAL', 'Dùng thử'),
        ('EXPIRED', 'Hết hạn'),
        ('CANCELLED', 'Đã hủy'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.UUIDField()
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Sub {self.id} (Patient: {self.patient_id}) - {self.status}"


class SubscriptionUsage(models.Model):
    """Tracks current utilization against quotas."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='usages')
    entitlement = models.ForeignKey(PlanEntitlement, on_delete=models.CASCADE)
    usage_limit = models.IntegerField(default=0, help_text="0 means unlimited or boolean")
    current_usage = models.IntegerField(default=0)
    reset_at = models.DateTimeField()

    class Meta:
        db_table = 'subscription_usages'
        unique_together = ('subscription', 'entitlement')

    def __str__(self):
        return f"Usage {self.entitlement.feature_code}: {self.current_usage}/{self.usage_limit}"
