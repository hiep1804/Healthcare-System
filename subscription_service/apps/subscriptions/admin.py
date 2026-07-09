from django.contrib import admin
from .models import Plan, PlanEntitlement, Subscription, SubscriptionUsage


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'billing_cycle', 'is_active')
    list_filter = ('billing_cycle', 'is_active')
    search_fields = ('name', 'code')


@admin.register(PlanEntitlement)
class PlanEntitlementAdmin(admin.ModelAdmin):
    list_display = ('plan', 'feature_code', 'value')
    list_filter = ('feature_code',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'plan', 'status', 'current_period_end', 'cancel_at_period_end')
    list_filter = ('status', 'cancel_at_period_end')
    search_fields = ('patient_id',)


@admin.register(SubscriptionUsage)
class SubscriptionUsageAdmin(admin.ModelAdmin):
    list_display = ('subscription', 'entitlement', 'usage_limit', 'current_usage', 'reset_at')
