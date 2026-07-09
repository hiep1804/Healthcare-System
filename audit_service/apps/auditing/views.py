from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from .models import AuditLog, AccessLog, SecurityEvent
from .serializers import (
    AuditLogSerializer, AccessLogSerializer, SecurityEventSerializer,
    AccessReportRequestSerializer
)
from common.permissions import IsAdmin


class AuditEventCreateView(APIView):
    """POST /api/v1/audit/events - Log audit event (System role or authorized service only)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AuditLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        audit_log = serializer.save()

        # If medical record was viewed, automatically create an AccessLog entry
        if audit_log.action == 'VIEW_MEDICAL_RECORD' and audit_log.resource_type == 'PATIENT_RECORD':
            AccessLog.objects.create(
                patient_id=audit_log.resource_id,
                accessed_by_user_id=audit_log.actor_user_id,
                accessed_by_role=audit_log.actor_role,
                action=audit_log.action,
                ip_address=audit_log.ip_address
            )

        return Response(AuditLogSerializer(audit_log).data, status=status.HTTP_201_CREATED)


class AuditEventSearchView(APIView):
    """GET /api/v1/audit/events - List/Search audit events (Admin only)"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        queryset = AuditLog.objects.all()

        actor_user_id = request.query_params.get('actor_user_id')
        if actor_user_id:
            queryset = queryset.filter(actor_user_id=actor_user_id)

        action = request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)

        serializer = AuditLogSerializer(queryset, many=True)
        return Response({'data': serializer.data})


class PatientAccessLogView(APIView):
    """GET /api/v1/audit/patients/{patient_id}/access-log - View access logs for patient (Admin only)"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, patient_id):
        logs = AccessLog.objects.filter(patient_id=patient_id)
        serializer = AccessLogSerializer(logs, many=True)
        return Response({'data': serializer.data})


class SecurityEventsView(APIView):
    """GET /api/v1/audit/security-events - View security events (Admin only)"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        events = SecurityEvent.objects.all()
        serializer = SecurityEventSerializer(events, many=True)
        return Response({'data': serializer.data})


class AccessReportView(APIView):
    """POST /api/v1/audit/reports/access - Generate access report (Admin only)"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        serializer = AccessReportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient_id = serializer.validated_data.get('patient_id')
        start_date = serializer.validated_data.get('start_date')
        end_date = serializer.validated_data.get('end_date')

        queryset = AccessLog.objects.all()
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        logs_data = AccessLogSerializer(queryset, many=True).data

        return Response({
            'report_name': 'Access Log Report',
            'generated_at': timezone.now().isoformat(),
            'total_entries': len(logs_data),
            'data': logs_data
        }, status=status.HTTP_200_OK)
