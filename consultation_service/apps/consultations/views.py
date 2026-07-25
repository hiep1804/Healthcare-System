from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Consultation, ClinicalNote, Diagnosis, Prescription, PrescriptionItem, AIDecision
from .serializers import (
    ConsultationSerializer, ConsultationCreateSerializer, ClinicalNoteSerializer,
    DiagnosisSerializer, PrescriptionSerializer, PrescriptionItemSerializer, AIDecisionSerializer
)
from common.permissions import IsDoctor, IsPatient, IsDoctorOrAdmin, IsPatientOrDoctor


class ConsultationListCreateView(APIView):
    """
    POST /api/v1/consultations - Create consultation from appointment (System/Doctor)
    GET /api/v1/consultations - List consultations
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Consultation.objects.all()

        query_params = getattr(request, 'query_params', getattr(request, 'GET', {}))
        appointment_id = query_params.get('appointment_id')
        if appointment_id:
            queryset = queryset.filter(appointment_id=appointment_id)

        patient_id = query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        provider_id = query_params.get('provider_id')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)

        serializer = ConsultationSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def post(self, request):
        appointment_id = request.data.get('appointment_id')
        if appointment_id:
            existing = Consultation.objects.filter(appointment_id=appointment_id).first()
            if existing:
                return Response(ConsultationSerializer(existing).data, status=status.HTTP_200_OK)

        serializer = ConsultationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        consultation = serializer.save()
        return Response(ConsultationSerializer(consultation).data, status=status.HTTP_201_CREATED)


class ConsultationDetailView(APIView):
    """GET /api/v1/consultations/{consultation_id} - View consultation (Patient/Doctor/Admin)"""
    permission_classes = [IsAuthenticated]

    def get(self, request, consultation_id):
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': {'code': 'CONSULTATION_NOT_FOUND', 'message': 'Không tìm thấy phiên khám.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ConsultationSerializer(consultation)
        return Response(serializer.data)


class ConsultationStartView(APIView):
    """PATCH /api/v1/consultations/{consultation_id}/start - Start consultation (Doctor only)"""
    permission_classes = [IsAuthenticated, IsDoctor]

    def patch(self, request, consultation_id):
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': {'code': 'CONSULTATION_NOT_FOUND', 'message': 'Không tìm thấy phiên khám.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        if consultation.status != 'DRAFT':
            return Response(
                {'error': {'code': 'INVALID_STATUS', 'message': 'Phiên khám phải ở trạng thái DRAFT để bắt đầu.'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        consultation.status = 'IN_PROGRESS'
        consultation.start_time = timezone.now()
        consultation.save()
        return Response(ConsultationSerializer(consultation).data)


class ConsultationCompleteView(APIView):
    """PATCH /api/v1/consultations/{consultation_id}/complete - Complete consultation (Doctor only)"""
    permission_classes = [IsAuthenticated, IsDoctor]

    def patch(self, request, consultation_id):
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': {'code': 'CONSULTATION_NOT_FOUND', 'message': 'Không tìm thấy phiên khám.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        if consultation.status != 'IN_PROGRESS':
            return Response(
                {'error': {'code': 'INVALID_STATUS', 'message': 'Phiên khám phải ở trạng thái IN_PROGRESS để hoàn tất.'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        consultation.status = 'COMPLETED'
        consultation.end_time = timezone.now()
        consultation.save()
        return Response(ConsultationSerializer(consultation).data)


class ClinicalNoteCreateView(APIView):
    """POST /api/v1/consultations/{consultation_id}/notes - Create/update clinical note (Doctor only)"""
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, consultation_id):
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': {'code': 'CONSULTATION_NOT_FOUND', 'message': 'Không tìm thấy phiên khám.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        clinical_note, created = ClinicalNote.objects.get_or_create(consultation=consultation)
        serializer = ClinicalNoteSerializer(clinical_note, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ClinicalNoteSerializer(clinical_note).data)


class DiagnosisCreateView(APIView):
    """POST /api/v1/consultations/{consultation_id}/diagnoses - Add diagnosis (Doctor only)"""
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, consultation_id):
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': {'code': 'CONSULTATION_NOT_FOUND', 'message': 'Không tìm thấy phiên khám.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DiagnosisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        diagnosis = serializer.save(consultation=consultation)
        return Response(DiagnosisSerializer(diagnosis).data, status=status.HTTP_201_CREATED)


class PrescriptionCreateGetView(APIView):
    """
    POST /api/v1/consultations/{consultation_id}/prescriptions - Create prescription (Doctor only)
    GET /api/v1/consultations/{consultation_id}/prescriptions - View prescription (Patient/Doctor)
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsDoctor()]
        return [IsAuthenticated(), IsPatientOrDoctor()]

    def get(self, request, consultation_id):
        try:
            prescription = Prescription.objects.get(consultation_id=consultation_id)
            serializer = PrescriptionSerializer(prescription)
            return Response(serializer.data)
        except Prescription.DoesNotExist:
            return Response({'id': None, 'notes': '', 'items': []}, status=status.HTTP_200_OK)

    def post(self, request, consultation_id):
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': {'code': 'CONSULTATION_NOT_FOUND', 'message': 'Không tìm thấy phiên khám.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        prescription, created = Prescription.objects.get_or_create(consultation=consultation)
        prescription.notes = request.data.get('notes', '')
        prescription.save()

        # Handle prescription items if provided
        items_data = request.data.get('items', [])
        if items_data:
            # Delete old items if updating
            prescription.items.all().delete()
            for item in items_data:
                serializer = PrescriptionItemSerializer(data=item)
                serializer.is_valid(raise_exception=True)
                serializer.save(prescription=prescription)

        return Response(PrescriptionSerializer(prescription).data, status=status.HTTP_201_CREATED)


class AIDecisionCreateView(APIView):
    """POST /api/v1/consultations/{consultation_id}/ai-decisions - Record choice on AI recommendation (Doctor only)"""
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, consultation_id):
        try:
            consultation = Consultation.objects.get(id=consultation_id)
        except Consultation.DoesNotExist:
            return Response(
                {'error': {'code': 'CONSULTATION_NOT_FOUND', 'message': 'Không tìm thấy phiên khám.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AIDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        decision = serializer.save(consultation=consultation)
        return Response(AIDecisionSerializer(decision).data, status=status.HTTP_201_CREATED)
