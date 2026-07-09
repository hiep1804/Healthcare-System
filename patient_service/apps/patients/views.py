from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Patient, Allergy, MedicalCondition, CurrentMedication, Consent
from .serializers import (
    PatientSerializer, PatientCreateSerializer, PatientUpdateSerializer,
    AllergySerializer, AllergyCreateSerializer,
    MedicalConditionSerializer, MedicalConditionCreateSerializer,
    CurrentMedicationSerializer, CurrentMedicationCreateSerializer,
    ConsentSerializer, ConsentCreateSerializer,
)
from common.permissions import IsPatientOrAdmin, IsPatientOrDoctor, IsPatient, IsDoctorOrAdmin
from common.pagination import StandardResultsSetPagination


class PatientCreateView(APIView):
    """POST /api/v1/patients - Create patient profile."""
    permission_classes = [IsAuthenticated, IsPatientOrAdmin]

    def post(self, request):
        serializer = PatientCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save()
        return Response(PatientSerializer(patient).data, status=status.HTTP_201_CREATED)


class PatientMeView(APIView):
    """GET /api/v1/patients/me - View own profile."""
    permission_classes = [IsAuthenticated, IsPatient]

    def get(self, request):
        try:
            patient = Patient.objects.get(user_id=request.user.id)
        except Patient.DoesNotExist:
            return Response(
                {'error': {'code': 'PATIENT_NOT_FOUND', 'message': 'Hồ sơ bệnh nhân chưa được tạo.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(PatientSerializer(patient).data)


class PatientDetailView(APIView):
    """
    GET /api/v1/patients/{patient_id} - View patient profile (Doctor/Admin).
    PATCH /api/v1/patients/{patient_id} - Update patient profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': {'code': 'PATIENT_NOT_FOUND', 'message': 'Không tìm thấy hồ sơ bệnh nhân.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(PatientSerializer(patient).data)

    def patch(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': {'code': 'PATIENT_NOT_FOUND', 'message': 'Không tìm thấy hồ sơ bệnh nhân.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PatientUpdateSerializer(patient, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(PatientSerializer(patient).data)


class AllergyListCreateView(APIView):
    """
    GET /api/v1/patients/{patient_id}/allergies - List allergies.
    POST /api/v1/patients/{patient_id}/allergies - Add allergy.
    """
    permission_classes = [IsAuthenticated, IsPatientOrDoctor]

    def get(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': {'code': 'PATIENT_NOT_FOUND', 'message': 'Không tìm thấy bệnh nhân.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        allergies = patient.allergies.filter(is_active=True)
        serializer = AllergySerializer(allergies, many=True)
        return Response({'data': serializer.data})

    def post(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': {'code': 'PATIENT_NOT_FOUND', 'message': 'Không tìm thấy bệnh nhân.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AllergyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        allergy = serializer.save(patient=patient)
        return Response(AllergySerializer(allergy).data, status=status.HTTP_201_CREATED)


class ConditionListCreateView(APIView):
    """
    GET /api/v1/patients/{patient_id}/conditions - List conditions.
    POST /api/v1/patients/{patient_id}/conditions - Add condition.
    """
    permission_classes = [IsAuthenticated, IsPatientOrDoctor]

    def get(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': {'code': 'PATIENT_NOT_FOUND', 'message': 'Không tìm thấy bệnh nhân.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        conditions = patient.conditions.all()
        serializer = MedicalConditionSerializer(conditions, many=True)
        return Response({'data': serializer.data})

    def post(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': {'code': 'PATIENT_NOT_FOUND', 'message': 'Không tìm thấy bệnh nhân.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = MedicalConditionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        condition = serializer.save(patient=patient)
        return Response(MedicalConditionSerializer(condition).data, status=status.HTTP_201_CREATED)


class MedicationListCreateView(APIView):
    """
    GET /api/v1/patients/{patient_id}/medications - List medications.
    POST /api/v1/patients/{patient_id}/medications - Add medication.
    """
    permission_classes = [IsAuthenticated, IsPatientOrDoctor]

    def get(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': {'code': 'PATIENT_NOT_FOUND', 'message': 'Không tìm thấy bệnh nhân.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        medications = patient.medications.filter(is_active=True)
        serializer = CurrentMedicationSerializer(medications, many=True)
        return Response({'data': serializer.data})

    def post(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': {'code': 'PATIENT_NOT_FOUND', 'message': 'Không tìm thấy bệnh nhân.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = CurrentMedicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        medication = serializer.save(patient=patient)
        return Response(CurrentMedicationSerializer(medication).data, status=status.HTTP_201_CREATED)


class ConsentCreateView(APIView):
    """POST /api/v1/patients/{patient_id}/consents - Grant consent."""
    permission_classes = [IsAuthenticated, IsPatient]

    def post(self, request, patient_id):
        try:
            patient = Patient.objects.get(id=patient_id)
        except Patient.DoesNotExist:
            return Response(
                {'error': {'code': 'PATIENT_NOT_FOUND', 'message': 'Không tìm thấy bệnh nhân.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ConsentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        consent = serializer.save(patient=patient)
        return Response(ConsentSerializer(consent).data, status=status.HTTP_201_CREATED)


class ConsentRevokeView(APIView):
    """DELETE /api/v1/patients/{patient_id}/consents/{consent_id} - Revoke consent."""
    permission_classes = [IsAuthenticated, IsPatient]

    def delete(self, request, patient_id, consent_id):
        try:
            consent = Consent.objects.get(id=consent_id, patient_id=patient_id, is_active=True)
        except Consent.DoesNotExist:
            return Response(
                {'error': {'code': 'CONSENT_NOT_FOUND', 'message': 'Không tìm thấy consent.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        consent.is_active = False
        consent.revoked_at = timezone.now()
        consent.save()
        return Response({'message': 'Đã thu hồi consent.'}, status=status.HTTP_200_OK)
