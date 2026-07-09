from rest_framework import serializers
from .models import Patient, Allergy, MedicalCondition, CurrentMedication, Consent


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'user_id', 'first_name', 'last_name', 'date_of_birth',
            'gender', 'phone', 'address', 'city', 'national_id',
            'insurance_number', 'emergency_contact_name',
            'emergency_contact_phone', 'blood_type',
        ]

    def validate_user_id(self, value):
        if Patient.objects.filter(user_id=value).exists():
            raise serializers.ValidationError("Hồ sơ bệnh nhân đã tồn tại cho user này.")
        return value


class PatientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'phone', 'address', 'city', 'national_id',
            'insurance_number', 'emergency_contact_name',
            'emergency_contact_phone', 'blood_type',
        ]


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = '__all__'
        read_only_fields = ['id', 'patient', 'created_at', 'updated_at']


class AllergyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = ['allergen', 'severity', 'reaction', 'note']


class MedicalConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalCondition
        fields = '__all__'
        read_only_fields = ['id', 'patient', 'created_at', 'updated_at']


class MedicalConditionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalCondition
        fields = ['condition_name', 'icd_code', 'status', 'diagnosed_date', 'note']


class CurrentMedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentMedication
        fields = '__all__'
        read_only_fields = ['id', 'patient', 'created_at', 'updated_at']


class CurrentMedicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrentMedication
        fields = [
            'drug_name', 'dosage', 'frequency', 'start_date',
            'end_date', 'prescribed_by', 'note',
        ]


class ConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consent
        fields = '__all__'
        read_only_fields = ['id', 'patient', 'granted_at', 'revoked_at']


class ConsentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consent
        fields = ['consent_type', 'granted_to_user_id', 'description']
