from django.utils import timezone
from datetime import timedelta, datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import ProviderSchedule, TimeSlot, Appointment, AppointmentStatusHistory
from .serializers import (
    ProviderScheduleSerializer, TimeSlotSerializer, AppointmentSerializer,
    HoldSlotSerializer, GenerateSlotsSerializer
)
from common.permissions import IsDoctor, IsAdmin, IsPatient, IsDoctorOrAdmin, IsPatientOrDoctorOrAdmin


class ScheduleListCreateView(APIView):
    """
    GET /api/v1/providers/{provider_id}/schedules - View schedule (Public)
    POST /api/v1/providers/{provider_id}/schedules - Create schedule (Doctor/Admin)
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsDoctorOrAdmin()]
        return [AllowAny()]

    def get(self, request, provider_id):
        schedules = ProviderSchedule.objects.filter(provider_id=provider_id, is_active=True)
        serializer = ProviderScheduleSerializer(schedules, many=True)
        return Response({'data': serializer.data})

    def post(self, request, provider_id):
        serializer = ProviderScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        schedule = serializer.save(provider_id=provider_id)
        return Response(ProviderScheduleSerializer(schedule).data, status=status.HTTP_201_CREATED)


class GenerateSlotsView(APIView):
    """POST /api/v1/providers/{provider_id}/slots/generate - Generate slots from schedules (Doctor/Admin)"""
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def post(self, request, provider_id):
        serializer = GenerateSlotsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']

        schedules = ProviderSchedule.objects.filter(provider_id=provider_id, is_active=True)
        if not schedules.exists():
            return Response(
                {'error': {'code': 'NO_SCHEDULES', 'message': 'Không tìm thấy lịch làm việc của bác sĩ.'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        slots_created = 0
        current_date = start_date
        while current_date <= end_date:
            weekday = current_date.weekday()  # Monday is 0, Sunday is 6
            day_schedules = schedules.filter(day_of_week=weekday)

            for sched in day_schedules:
                # Basic generation: create time slots of 30 mins each
                # Or based on start_time and end_time
                start_dt = datetime.combine(current_date, sched.start_time)
                end_dt = datetime.combine(current_date, sched.end_time)

                current_slot_start = start_dt
                while current_slot_start + timedelta(minutes=30) <= end_dt:
                    current_slot_end = current_slot_start + timedelta(minutes=30)

                    # Create if not exists
                    _, created = TimeSlot.objects.get_or_create(
                        provider_id=provider_id,
                        date=current_date,
                        start_time=current_slot_start.time(),
                        end_time=current_slot_end.time(),
                        defaults={'status': 'FREE'}
                    )
                    if created:
                        slots_created += 1

                    current_slot_start = current_slot_end

            current_date += timedelta(days=1)

        return Response({
            'message': f'Đã sinh {slots_created} slot khám thành công.',
            'slots_created': slots_created
        }, status=status.HTTP_201_CREATED)


class SlotListView(APIView):
    """GET /api/v1/providers/{provider_id}/slots - View free slots (Public)"""
    permission_classes = [AllowAny]

    def get(self, request, provider_id):
        # Filter and clean up expired holds
        now = timezone.now()
        TimeSlot.objects.filter(status='HELD', hold_expires_at__lt=now).update(
            status='FREE', hold_expires_at=None
        )

        slots = TimeSlot.objects.filter(provider_id=provider_id, status='FREE')
        serializer = TimeSlotSerializer(slots, many=True)
        return Response({'data': serializer.data})


class HoldSlotView(APIView):
    """POST /api/v1/appointments/hold - Hold slot temporarily (Patient only)"""
    permission_classes = [IsAuthenticated, IsPatient]

    def post(self, request):
        serializer = HoldSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        slot_id = serializer.validated_data['slot_id']
        try:
            slot = TimeSlot.objects.get(id=slot_id)
        except TimeSlot.DoesNotExist:
            return Response(
                {'error': {'code': 'SLOT_NOT_FOUND', 'message': 'Không tìm thấy khung giờ.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        # Release expired holds first
        if slot.status == 'HELD' and slot.hold_expires_at and slot.hold_expires_at < timezone.now():
            slot.status = 'FREE'
            slot.hold_expires_at = None
            slot.save()

        if slot.status != 'FREE':
            return Response(
                {'error': {'code': 'SLOT_NOT_AVAILABLE', 'message': 'Khung giờ đã được đặt hoặc đang được giữ.'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        hold_duration = timedelta(minutes=10)
        hold_expiry = timezone.now() + hold_duration

        slot.status = 'HELD'
        slot.hold_expires_at = hold_expiry
        slot.save()

        appointment = Appointment.objects.create(
            patient_id=serializer.validated_data['patient_id'],
            provider_id=serializer.validated_data['provider_id'],
            slot=slot,
            service_id=serializer.validated_data['service_id'],
            status='HELD',
            hold_expires_at=hold_expiry,
            amount=serializer.validated_data['amount'],
            currency=serializer.validated_data['currency'],
        )

        AppointmentStatusHistory.objects.create(
            appointment=appointment,
            status='HELD',
            notes='Giữ chỗ tạm thời trong 10 phút.',
            changed_by=request.user.id
        )

        return Response({
            'appointment_id': str(appointment.id),
            'status': 'HELD',
            'hold_expires_at': hold_expiry.isoformat(),
            'amount': float(appointment.amount),
            'currency': appointment.currency
        }, status=status.HTTP_201_CREATED)


class AppointmentListCreateView(APIView):
    """
    POST /api/v1/appointments - Create/Confirm appointment booking
    GET /api/v1/appointments - List appointments for user (Patient/Doctor/Admin)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = Appointment.objects.all()

        # If patient, filter by patient_id. In production, we'd look up the patient profile via user_id
        # For simplicity in testing, let's filter if query param provided or custom headers exist.
        patient_id = request.query_params.get('patient_id')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        provider_id = request.query_params.get('provider_id')
        if provider_id:
            queryset = queryset.filter(provider_id=provider_id)

        serializer = AppointmentSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def post(self, request):
        # Direct appointment creation (no hold) or updating HELD to PAYMENT_PENDING
        appointment_id = request.data.get('appointment_id')
        if appointment_id:
            try:
                appt = Appointment.objects.get(id=appointment_id)
            except Appointment.DoesNotExist:
                return Response(
                    {'error': {'code': 'APPOINTMENT_NOT_FOUND', 'message': 'Không tìm thấy lịch hẹn.'}},
                    status=status.HTTP_404_NOT_FOUND
                )

            if appt.status != 'HELD':
                return Response(
                    {'error': {'code': 'INVALID_STATUS', 'message': 'Trạng thái lịch hẹn không hợp lệ để tạo.'}},
                    status=status.HTTP_400_BAD_REQUEST
                )

            appt.status = 'PAYMENT_PENDING'
            appt.hold_expires_at = None
            appt.save()

            appt.slot.status = 'BOOKED'
            appt.slot.hold_expires_at = None
            appt.slot.save()

            AppointmentStatusHistory.objects.create(
                appointment=appt,
                status='PAYMENT_PENDING',
                notes='Chờ thanh toán phí khám.',
                changed_by=request.user.id
            )
            return Response(AppointmentSerializer(appt).data)
        else:
            # Create a direct booking (mock payments or free visits)
            return Response(
                {'error': {'code': 'APPOINTMENT_ID_REQUIRED', 'message': 'Yêu cầu truyền appointment_id đã được HELD.'}},
                status=status.HTTP_400_BAD_REQUEST
            )


class AppointmentDetailView(APIView):
    """GET /api/v1/appointments/{appointment_id} - View appointment detail"""
    permission_classes = [IsAuthenticated, IsPatientOrDoctorOrAdmin]

    def get(self, request, appointment_id):
        try:
            appt = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response(
                {'error': {'code': 'APPOINTMENT_NOT_FOUND', 'message': 'Không tìm thấy lịch hẹn.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AppointmentSerializer(appt)
        return Response(serializer.data)


class AppointmentCancelView(APIView):
    """PATCH /api/v1/appointments/{appointment_id}/cancel - Cancel appointment"""
    permission_classes = [IsAuthenticated, IsPatientOrDoctorOrAdmin]

    def patch(self, request, appointment_id):
        try:
            appt = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response(
                {'error': {'code': 'APPOINTMENT_NOT_FOUND', 'message': 'Không tìm thấy lịch hẹn.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        if appt.status in ['CANCELLED', 'COMPLETED', 'REFUNDED']:
            return Response(
                {'error': {'code': 'ALREADY_FINALIZED', 'message': 'Lịch hẹn đã hoàn tất hoặc đã hủy.'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        appt.status = 'CANCELLED'
        appt.save()

        # Free the slot
        appt.slot.status = 'FREE'
        appt.slot.hold_expires_at = None
        appt.slot.save()

        AppointmentStatusHistory.objects.create(
            appointment=appt,
            status='CANCELLED',
            notes=request.data.get('notes', 'Bệnh nhân hoặc Bác sĩ hủy lịch.'),
            changed_by=request.user.id
        )

        return Response(AppointmentSerializer(appt).data)


class AppointmentConfirmView(APIView):
    """PATCH /api/v1/appointments/{appointment_id}/confirm - Confirm appointment post-payment (System only)"""
    permission_classes = [IsAuthenticated]  # gateway/internal system call

    def patch(self, request, appointment_id):
        try:
            appt = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response(
                {'error': {'code': 'APPOINTMENT_NOT_FOUND', 'message': 'Không tìm thấy lịch hẹn.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        appt.status = 'CONFIRMED'
        appt.save()

        appt.slot.status = 'BOOKED'
        appt.slot.save()

        AppointmentStatusHistory.objects.create(
            appointment=appt,
            status='CONFIRMED',
            notes='Thanh toán thành công. Lịch hẹn được xác nhận.',
            changed_by=request.user.id
        )

        return Response(AppointmentSerializer(appt).data)


class AppointmentCompleteView(APIView):
    """PATCH /api/v1/appointments/{appointment_id}/complete - Complete consultation (Doctor only)"""
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def patch(self, request, appointment_id):
        try:
            appt = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response(
                {'error': {'code': 'APPOINTMENT_NOT_FOUND', 'message': 'Không tìm thấy lịch hẹn.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        if appt.status != 'CONFIRMED':
            return Response(
                {'error': {'code': 'INVALID_STATUS', 'message': 'Lịch hẹn phải ở trạng thái CONFIRMED để hoàn tất.'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        appt.status = 'COMPLETED'
        appt.save()

        AppointmentStatusHistory.objects.create(
            appointment=appt,
            status='COMPLETED',
            notes='Bác sĩ đã hoàn tất phiên khám.',
            changed_by=request.user.id
        )

        return Response(AppointmentSerializer(appt).data)
