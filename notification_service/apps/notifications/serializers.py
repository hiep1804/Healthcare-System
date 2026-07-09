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
    recipient_user_id = serializers.UUIDField()
    channel = serializers.ChoiceField(choices=['SMS', 'EMAIL', 'PUSH'])
    template_code = serializers.CharField(max_length=100)
    recipient_address = serializers.CharField(max_length=250)
    variables = serializers.JSONField(default=dict, required=False)
