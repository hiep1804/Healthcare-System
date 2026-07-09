import re
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import NotificationTemplate, NotificationJob, DeliveryLog
from .serializers import (
    NotificationTemplateSerializer, NotificationJobSerializer,
    SendNotificationSerializer
)
from common.permissions import IsAdmin


class TemplateListCreateView(APIView):
    """
    GET /api/v1/notification-templates - List templates (Admin only)
    POST /api/v1/notification-templates - Create template (Admin only)
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        templates = NotificationTemplate.objects.all()
        serializer = NotificationTemplateSerializer(templates, many=True)
        return Response({'data': serializer.data})

    def post(self, request):
        serializer = NotificationTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        template = serializer.save()
        return Response(NotificationTemplateSerializer(template).data, status=status.HTTP_201_CREATED)


class TemplateDetailView(APIView):
    """PATCH /api/v1/notification-templates/{template_id} - Update template (Admin only)"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, template_id):
        try:
            template = NotificationTemplate.objects.get(id=template_id)
        except NotificationTemplate.DoesNotExist:
            return Response(
                {'error': {'code': 'TEMPLATE_NOT_FOUND', 'message': 'Không tìm thấy mẫu thông báo.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = NotificationTemplateSerializer(template, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(NotificationTemplateSerializer(template).data)


class SendNotificationView(APIView):
    """POST /api/v1/notifications/send - Send a notification using templates (System/Admin)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        template_code = serializer.validated_data['template_code']
        channel = serializer.validated_data['channel']
        recipient_user_id = serializer.validated_data['recipient_user_id']
        recipient_address = serializer.validated_data['recipient_address']
        variables = serializer.validated_data.get('variables', {})

        try:
            template = NotificationTemplate.objects.get(code=template_code, channel=channel)
        except NotificationTemplate.DoesNotExist:
            return Response(
                {'error': {'code': 'TEMPLATE_NOT_FOUND', 'message': f'Không tìm thấy template {template_code} cho kênh {channel}.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        # Render basic template variables: e.g. {{patient_name}} -> Nguyễn Văn A
        rendered_body = template.body_template
        for k, v in variables.items():
            rendered_body = rendered_body.replace(f'{{{{{k}}}}}', str(v))

        # Create job
        job = NotificationJob.objects.create(
            template=template,
            recipient_user_id=recipient_user_id,
            channel=channel,
            recipient_address=recipient_address,
            variables=variables,
            status='SENT',  # Mocks immediate transmission
            sent_at=timezone.now()
        )

        DeliveryLog.objects.create(
            job=job,
            status='SUCCESS',
            response_payload=f"Gửi thành công qua {channel}. Nội dung: {rendered_body}"
        )

        return Response({
            'message': 'Đã gửi thông báo thành công.',
            'job_id': str(job.id),
            'rendered_content': rendered_body
        }, status=status.HTTP_201_CREATED)


class JobDetailView(APIView):
    """GET /api/v1/notification-jobs/{job_id} - View job status (Admin/System)"""
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            job = NotificationJob.objects.get(id=job_id)
        except NotificationJob.DoesNotExist:
            return Response(
                {'error': {'code': 'JOB_NOT_FOUND', 'message': 'Không tìm thấy tiến trình gửi thông báo.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = NotificationJobSerializer(job)
        return Response(serializer.data)


class JobRetryView(APIView):
    """POST /api/v1/notification-jobs/{job_id}/retry - Retry sending (Admin/System)"""
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        try:
            job = NotificationJob.objects.get(id=job_id)
        except NotificationJob.DoesNotExist:
            return Response(
                {'error': {'code': 'JOB_NOT_FOUND', 'message': 'Không tìm thấy tiến trình gửi thông báo.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        job.status = 'SENT'
        job.sent_at = timezone.now()
        job.error_message = ""
        job.save()

        DeliveryLog.objects.create(
            job=job,
            status='SUCCESS',
            response_payload="Thử lại gửi thành công (Mock)."
        )

        return Response({
            'message': 'Đã thử lại gửi thông báo.',
            'job': NotificationJobSerializer(job).data
        })
