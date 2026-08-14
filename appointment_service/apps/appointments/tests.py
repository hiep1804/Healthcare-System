import uuid
from datetime import date, time, timedelta
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

from apps.appointments.models import ProviderSchedule, TimeSlot, Appointment, AppointmentStatusHistory


class AppointmentBookingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.provider_id = uuid.uuid4()
        self.patient_id = uuid.uuid4()
        self.service_id = uuid.uuid4()

        now_local = timezone.localtime(timezone.now())
        self.today = now_local.date()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)

        # Create past slot
        self.past_slot = TimeSlot.objects.create(
            provider_id=self.provider_id,
            date=self.yesterday,
            start_time=time(9, 0),
            end_time=time(9, 30),
            status='FREE'
        )

        # Create future slot
        self.future_slot = TimeSlot.objects.create(
            provider_id=self.provider_id,
            date=self.tomorrow,
            start_time=time(10, 0),
            end_time=time(10, 30),
            status='FREE'
        )

    def test_slot_list_view_filters_out_past_slots(self):
        """Past slots should not be returned in GET /api/v1/appointments/providers/{provider_id}/slots"""
        url = f'/api/v1/appointments/providers/{self.provider_id}/slots'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        slot_ids = [slot['id'] for slot in response.data.get('data', [])]
        self.assertIn(str(self.future_slot.id), slot_ids)
        self.assertNotIn(str(self.past_slot.id), slot_ids)

    def test_rebook_cancelled_appointment_slot(self):
        """Cancelling an appointment frees the slot and allows rebooking it"""
        # Step 1: Initial booking of future_slot
        appt1 = Appointment.objects.create(
            patient_id=self.patient_id,
            provider_id=self.provider_id,
            slot=self.future_slot,
            service_id=self.service_id,
            status='CONFIRMED',
            amount=300000,
            currency='VND'
        )
        self.future_slot.status = 'BOOKED'
        self.future_slot.save()

        # Step 2: Cancel appointment
        appt1.status = 'CANCELLED'
        appt1.save()

        self.future_slot.status = 'FREE'
        self.future_slot.save()

        self.future_slot.refresh_from_db()
        self.assertEqual(self.future_slot.status, 'FREE')

        # Step 3: Re-book the same slot again
        appt2 = Appointment.objects.create(
            patient_id=self.patient_id,
            provider_id=self.provider_id,
            slot=self.future_slot,
            service_id=self.service_id,
            status='HELD',
            amount=300000,
            currency='VND'
        )
        self.assertIsNotNone(appt2.id)
        self.assertNotEqual(appt1.id, appt2.id)
        self.assertEqual(appt2.slot.id, self.future_slot.id)

    def test_auto_cancel_expired_appointments_and_hide_cancelled(self):
        """Past uncompleted appointments should be auto-cancelled and excluded from list view"""
        past_appt = Appointment.objects.create(
            patient_id=self.patient_id,
            provider_id=self.provider_id,
            slot=self.past_slot,
            service_id=self.service_id,
            status='HELD',
            amount=300000,
            currency='VND'
        )

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.client.force_authenticate(user=user)

        response = self.client.get('/api/v1/appointments')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        past_appt.refresh_from_db()
        self.assertEqual(past_appt.status, 'CANCELLED')

        returned_ids = [a['id'] for a in response.data.get('data', [])]
        self.assertNotIn(str(past_appt.id), returned_ids)
