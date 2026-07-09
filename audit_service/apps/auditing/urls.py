from django.urls import path
from .views import AuditEventCreateView, AuditEventSearchView, PatientAccessLogView, SecurityEventsView, AccessReportView

urlpatterns = [
    path('audit/events', AuditEventCreateView.as_view(), name='audit-event-create'),
    path('audit/search', AuditEventSearchView.as_view(), name='audit-event-search'),
    path('audit/patients/<uuid:patient_id>/access-log', PatientAccessLogView.as_view(), name='patient-access-log'),
    path('audit/security-events', SecurityEventsView.as_view(), name='security-events'),
    path('audit/reports/access', AccessReportView.as_view(), name='access-report'),
]
