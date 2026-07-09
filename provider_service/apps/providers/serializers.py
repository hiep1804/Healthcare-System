from rest_framework import serializers
from .models import Specialty, Clinic, Provider, DoctorLicense, ProviderService


class SpecialtySerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialty
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class DoctorLicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorLicense
        fields = '__all__'
        read_only_fields = ['id', 'provider', 'is_verified', 'created_at']


class ProviderServiceSerializer(serializers.ModelSerializer):
    specialty_name = serializers.CharField(source='specialty.name', read_only=True)

    class Meta:
        model = ProviderService
        fields = '__all__'
        read_only_fields = ['id', 'provider', 'created_at', 'updated_at']


class ProviderSerializer(serializers.ModelSerializer):
    clinic_detail = ClinicSerializer(source='clinic', read_only=True)
    services = ProviderServiceSerializer(many=True, read_only=True)
    licenses = DoctorLicenseSerializer(many=True, read_only=True)

    class Meta:
        model = Provider
        fields = '__all__'
        read_only_fields = ['id', 'rating', 'status', 'verification_notes', 'created_at', 'updated_at']


class ProviderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['user_id', 'first_name', 'last_name', 'bio', 'location', 'clinic']

    def validate_user_id(self, value):
        if Provider.objects.filter(user_id=value).exists():
            raise serializers.ValidationError("Hồ sơ bác sĩ đã tồn tại.")
        return value


class VerificationSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=['VERIFIED', 'REJECTED', 'NEED_MORE_INFO'])
    notes = serializers.CharField(required=False, allow_blank=True)
