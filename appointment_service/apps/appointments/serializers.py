from rest_framework import serializers
from .models import ProviderSchedule, TimeSlot, Appointment, AppointmentStatusHistory


class ProviderScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderSchedule
        fields = '__all__'
        read_only_fields = ['id', 'provider_id', 'created_at', 'updated_at']


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = '__all__'
        read_only_fields = ['id', 'provider_id', 'created_at']


class AppointmentStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentStatusHistory
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    slot_detail = TimeSlotSerializer(source='slot', read_only=True)
    status_history = AppointmentStatusHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['id', 'status', 'hold_expires_at', 'created_at', 'updated_at']


class HoldSlotSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()
    provider_id = serializers.UUIDField()
    slot_id = serializers.UUIDField()
    service_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    currency = serializers.CharField(max_length=10, default='VND')


class GenerateSlotsSerializer(serializers.Serializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()
