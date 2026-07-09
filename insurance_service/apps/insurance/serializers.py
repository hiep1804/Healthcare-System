from rest_framework import serializers
from .models import InsurancePolicy, EligibilityCheck, Claim, ClaimItem


class InsurancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsurancePolicy
        fields = '__all__'
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class EligibilityCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = EligibilityCheck
        fields = '__all__'
        read_only_fields = ['id', 'check_date']


class ClaimItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaimItem
        fields = '__all__'
        read_only_fields = ['id', 'claim']


class ClaimSerializer(serializers.ModelSerializer):
    items = ClaimItemSerializer(many=True, read_only=True)

    class Meta:
        model = Claim
        fields = '__all__'
        read_only_fields = ['id', 'status', 'processed_at', 'created_at']


class ClaimCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = ['patient_id', 'policy', 'appointment_id', 'total_amount', 'claimed_amount']


class EligibilityRequestSerializer(serializers.Serializer):
    patient_id = serializers.UUIDField()
    provider_id = serializers.UUIDField()
    policy_number = serializers.CharField(max_length=100)
