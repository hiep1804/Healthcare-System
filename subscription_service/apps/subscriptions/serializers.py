from rest_framework import serializers
from .models import Plan, PlanEntitlement, Subscription, SubscriptionUsage


class PlanEntitlementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanEntitlement
        fields = '__all__'
        read_only_fields = ['id', 'plan']


class PlanSerializer(serializers.ModelSerializer):
    entitlements = PlanEntitlementSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionUsageSerializer(serializers.ModelSerializer):
    feature_code = serializers.CharField(source='entitlement.feature_code', read_only=True)

    class Meta:
        model = SubscriptionUsage
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    usages = SubscriptionUsageSerializer(many=True, read_only=True)
    plan_detail = PlanSerializer(source='plan', read_only=True)

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['id', 'status', 'current_period_start', 'current_period_end', 'cancel_at_period_end', 'created_at', 'updated_at']


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['patient_id', 'plan']
