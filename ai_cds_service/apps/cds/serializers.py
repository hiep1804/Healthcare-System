from rest_framework import serializers
from .models import (
    Disease, Symptom, Drug, DrugInteraction,
    CDSConversation, CDSMessage, CDSRecommendation
)


class DiseaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disease
        fields = '__all__'


class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = '__all__'


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = '__all__'


class DrugInteractionSerializer(serializers.ModelSerializer):
    drug_a_detail = DrugSerializer(source='drug_a', read_only=True)
    drug_b_detail = DrugSerializer(source='drug_b', read_only=True)

    class Meta:
        model = DrugInteraction
        fields = '__all__'


class CDSRecommendationSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    action_display = serializers.CharField(source='get_doctor_action_display', read_only=True)

    class Meta:
        model = CDSRecommendation
        fields = '__all__'


class CDSMessageSerializer(serializers.ModelSerializer):
    recommendations = CDSRecommendationSerializer(many=True, read_only=True)

    class Meta:
        model = CDSMessage
        fields = '__all__'


class CDSConversationSerializer(serializers.ModelSerializer):
    messages = CDSMessageSerializer(many=True, read_only=True)
    recommendations = CDSRecommendationSerializer(many=True, read_only=True)

    class Meta:
        model = CDSConversation
        fields = '__all__'


class CDSConversationCreateSerializer(serializers.Serializer):
    consultation_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    patient_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    provider_id = serializers.UUIDField(required=False, allow_null=True, default=None)
    force_new = serializers.BooleanField(required=False, default=True)


class SendMessageSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)


class ActOnRecommendationSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['ACCEPTED', 'IGNORED', 'EDITED'])
    doctor_note = serializers.CharField(required=False, allow_blank=True, default='')


class DrugCheckRequestSerializer(serializers.Serializer):
    drug_names = serializers.ListField(child=serializers.CharField(), required=True)
    patient_allergies = serializers.ListField(child=serializers.CharField(), required=False, default=[])
