from django.urls import path
from .views import (
    ScheduleListCreateView, GenerateSlotsView, SlotListView, HoldSlotView,
    AppointmentListCreateView, AppointmentDetailView, AppointmentCancelView,
    AppointmentConfirmView, AppointmentCompleteView
)

urlpatterns = [
    path('providers/<uuid:provider_id>/schedules', ScheduleListCreateView.as_view(), name='schedule-list-create'),
    path('providers/<uuid:provider_id>/slots/generate', GenerateSlotsView.as_view(), name='slots-generate'),
    path('providers/<uuid:provider_id>/slots', SlotListView.as_view(), name='slots-list'),
    path('appointments/hold', HoldSlotView.as_view(), name='appointment-hold'),
    path('appointments', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<uuid:appointment_id>', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<uuid:appointment_id>/cancel', AppointmentCancelView.as_view(), name='appointment-cancel'),
    path('appointments/<uuid:appointment_id>/confirm', AppointmentConfirmView.as_view(), name='appointment-confirm'),
    path('appointments/<uuid:appointment_id>/complete', AppointmentCompleteView.as_view(), name='appointment-complete'),
]
