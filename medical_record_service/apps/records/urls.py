from django.urls import path
from .views import (
    PatientRecordTimelineView, PatientDocumentUploadView, DocumentDetailView,
    DocumentParseLabView, PatientLabResultListCreateView, PatientVitalsListCreateView
)

urlpatterns = [
    path('patients/<uuid:patient_id>/records', PatientRecordTimelineView.as_view(), name='patient-records'),
    path('patients/<uuid:patient_id>/documents', PatientDocumentUploadView.as_view(), name='patient-documents'),
    path('documents/<uuid:document_id>', DocumentDetailView.as_view(), name='document-detail'),
    path('documents/<uuid:document_id>/parse-lab', DocumentParseLabView.as_view(), name='document-parse-lab'),
    path('patients/<uuid:patient_id>/lab-results', PatientLabResultListCreateView.as_view(), name='patient-lab-results'),
    path('patients/<uuid:patient_id>/vitals', PatientVitalsListCreateView.as_view(), name='patient-vitals'),
]
