from rest_framework import serializers
from .models import Consultation, ClinicalNote, Diagnosis, Prescription, PrescriptionItem, AIDecision


class ClinicalNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalNote
        fields = '__all__'
        read_only_fields = ['id', 'consultation', 'created_at', 'updated_at']


class DiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnosis
        fields = '__all__'
        read_only_fields = ['id', 'consultation', 'created_at']


class PrescriptionItemSerializer(serializers.ModelSerializer):
    duration_days = serializers.IntegerField(required=False, default=5)
    quantity = serializers.IntegerField(required=False, default=10)
    dosage = serializers.CharField(required=False, default='1 viên', allow_blank=True)
    frequency = serializers.CharField(required=False, default='2 lần/ngày', allow_blank=True)

    class Meta:
        model = PrescriptionItem
        fields = '__all__'
        read_only_fields = ['id', 'prescription']


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['id', 'consultation', 'issued_at', 'created_at']


class AIDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIDecision
        fields = '__all__'
        read_only_fields = ['id', 'consultation', 'created_at']


class ConsultationSerializer(serializers.ModelSerializer):
    clinical_note = ClinicalNoteSerializer(read_only=True)
    diagnoses = DiagnosisSerializer(many=True, read_only=True)
    prescription = PrescriptionSerializer(read_only=True)
    ai_decisions = AIDecisionSerializer(many=True, read_only=True)

    class Meta:
        model = Consultation
        fields = '__all__'
        read_only_fields = ['id', 'status', 'start_time', 'end_time', 'created_at', 'updated_at']


class ConsultationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = ['appointment_id', 'patient_id', 'provider_id']
