from rest_framework import serializers
from .models import MedicalRecord, MedicalDocument, LabResult, LabResultItem, Vitals


class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalDocument
        fields = '__all__'
        read_only_fields = ['id', 'is_parsed', 'created_at']


class LabResultItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LabResultItem
        fields = '__all__'
        read_only_fields = ['id', 'lab_result']


class LabResultSerializer(serializers.ModelSerializer):
    items = LabResultItemSerializer(many=True, read_only=True)

    class Meta:
        model = LabResult
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class VitalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vitals
        fields = '__all__'
        read_only_fields = ['id', 'patient_id', 'recorded_by', 'created_at', 'recorded_at']
