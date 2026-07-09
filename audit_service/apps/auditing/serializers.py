from rest_framework import serializers
from .models import AuditLog, AccessLog, SecurityEvent


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AccessLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessLog
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class SecurityEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecurityEvent
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class AccessReportRequestSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
