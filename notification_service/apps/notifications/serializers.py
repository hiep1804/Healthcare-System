from rest_framework import serializers
from .models import NotificationTemplate, NotificationJob, DeliveryLog


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class DeliveryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryLog
        fields = '__all__'


class NotificationJobSerializer(serializers.ModelSerializer):
    delivery_logs = DeliveryLogSerializer(many=True, read_only=True)

    class Meta:
        model = NotificationJob
        fields = '__all__'
        read_only_fields = ['id', 'status', 'error_message', 'sent_at', 'created_at']


class SendNotificationSerializer(serializers.Serializer):
    recipient_user_id = serializers.UUIDField(required=False, allow_null=True)
    channel = serializers.ChoiceField(choices=['SMS', 'EMAIL', 'PUSH'], default='EMAIL')
    template_code = serializers.CharField(max_length=100, required=False, allow_blank=True, default='GENERAL_EMAIL')
    recipient_address = serializers.CharField(max_length=250)
    subject = serializers.CharField(max_length=250, required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    variables = serializers.JSONField(default=dict, required=False)
