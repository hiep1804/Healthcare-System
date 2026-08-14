from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import MedicalRecord, MedicalDocument, LabResult, LabResultItem, Vitals
from .serializers import (
    MedicalRecordSerializer, MedicalDocumentSerializer,
    LabResultSerializer, LabResultItemSerializer, VitalsSerializer
)
from common.permissions import IsPatientOrDoctor, IsDoctorOrAdmin, IsPatientOrDoctorOrAdmin


class PatientRecordTimelineView(APIView):
    """
    GET /api/v1/patients/{patient_id}/records - View timeline (Patient/Doctor)
    POST /api/v1/patients/{patient_id}/records - Create health record (Doctor/System)
    """
    permission_classes = [IsAuthenticated, IsPatientOrDoctor]

    def get(self, request, patient_id):
        records = MedicalRecord.objects.filter(patient_id=patient_id)
        serializer = MedicalRecordSerializer(records, many=True)
        return Response({'data': serializer.data})

    def post(self, request, patient_id):
        serializer = MedicalRecordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = serializer.save(patient_id=patient_id, created_by=request.user.id)
        return Response(MedicalRecordSerializer(record).data, status=status.HTTP_201_CREATED)


class PatientDocumentUploadView(APIView):
    """POST /api/v1/patients/{patient_id}/documents - Upload medical document (Patient/Doctor)"""
    permission_classes = [IsAuthenticated, IsPatientOrDoctor]

    def post(self, request, patient_id):
        serializer = MedicalDocumentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doc = serializer.save(patient_id=patient_id, uploaded_by=request.user.id)
        return Response(MedicalDocumentSerializer(doc).data, status=status.HTTP_201_CREATED)


class DocumentDetailView(APIView):
    """GET /api/v1/documents/{document_id} - View document metadata (Patient/Doctor)"""
    permission_classes = [IsAuthenticated, IsPatientOrDoctorOrAdmin]

    def get(self, request, document_id):
        try:
            doc = MedicalDocument.objects.get(id=document_id)
        except MedicalDocument.DoesNotExist:
            return Response(
                {'error': {'code': 'DOCUMENT_NOT_FOUND', 'message': 'Không tìm thấy tài liệu.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = MedicalDocumentSerializer(doc)
        return Response(serializer.data)


class DocumentParseLabView(APIView):
    """POST /api/v1/documents/{document_id}/parse-lab - Call OCR/parse lab report (Doctor/System)"""
    permission_classes = [IsAuthenticated]

    def post(self, request, document_id):
        try:
            doc = MedicalDocument.objects.get(id=document_id)
        except MedicalDocument.DoesNotExist:
            return Response(
                {'error': {'code': 'DOCUMENT_NOT_FOUND', 'message': 'Không tìm thấy tài liệu.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        if doc.document_type != 'LAB_RESULT':
            return Response(
                {'error': {'code': 'INVALID_DOCUMENT_TYPE', 'message': 'Tài liệu không phải kết quả xét nghiệm.'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        doc.is_parsed = True
        doc.save()

        # Mock OCR/Parsing: generate a parsed lab result
        import datetime
        lab_result = LabResult.objects.create(
            patient_id=doc.patient_id,
            test_date=datetime.date.today(),
            laboratory_name="Phòng xét nghiệm Trung tâm (Mock OCR)",
            notes=f"Tự động trích xuất từ tài liệu {doc.file_name}."
        )

        items_to_create = [
            {"test_name": "Glucose", "value": "5.8", "unit": "mmol/L", "reference_range": "3.9-6.4", "status": "NORMAL"},
            {"test_name": "Cholesterol toàn phần", "value": "6.2", "unit": "mmol/L", "reference_range": "3.9-5.2", "status": "HIGH"},
            {"test_name": "Triglycerides", "value": "2.4", "unit": "mmol/L", "reference_range": "0.46-1.88", "status": "HIGH"},
        ]

        for item in items_to_create:
            LabResultItem.objects.create(
                lab_result=lab_result,
                test_name=item["test_name"],
                value=item["value"],
                unit=item["unit"],
                reference_range=item["reference_range"],
                status=item["status"]
            )

        return Response({
            'message': 'Phân tích tài liệu xét nghiệm thành công.',
            'lab_result': LabResultSerializer(lab_result).data
        }, status=status.HTTP_200_OK)


class PatientLabResultListCreateView(APIView):
    """
    POST /api/v1/patients/{patient_id}/lab-results - Create lab result structured (Doctor/System)
    GET /api/v1/patients/{patient_id}/lab-results - View lab results (Patient/Doctor)
    """
    permission_classes = [IsAuthenticated, IsPatientOrDoctor]

    def get(self, request, patient_id):
        results = LabResult.objects.filter(patient_id=patient_id)
        serializer = LabResultSerializer(results, many=True)
        return Response({'data': serializer.data})

    def post(self, request, patient_id):
        serializer = LabResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lab_result = serializer.save(patient_id=patient_id)

        items_data = request.data.get('items', [])
        for item in items_data:
            item_serializer = LabResultItemSerializer(data=item)
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save(lab_result=lab_result)

        return Response(LabResultSerializer(lab_result).data, status=status.HTTP_201_CREATED)


class PatientVitalsListCreateView(APIView):
    """
    POST /api/v1/patients/{patient_id}/vitals - Record vital signs (Patient/Doctor)
    GET /api/v1/patients/{patient_id}/vitals - View vital signs (Patient/Doctor)
    """
    permission_classes = [IsAuthenticated, IsPatientOrDoctor]

    def get(self, request, patient_id):
        vitals = Vitals.objects.filter(patient_id=patient_id)
        serializer = VitalsSerializer(vitals, many=True)
        return Response({'data': serializer.data})

    def post(self, request, patient_id):
        data = dict(request.data)
        if 'temperature_celsius' in data and 'temperature_c' not in data:
            data['temperature_c'] = data['temperature_celsius']
        serializer = VitalsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        rec_by = getattr(request.user, 'id', None) or patient_id
        vitals = serializer.save(patient_id=patient_id, recorded_by=rec_by)
        return Response(VitalsSerializer(vitals).data, status=status.HTTP_201_CREATED)
