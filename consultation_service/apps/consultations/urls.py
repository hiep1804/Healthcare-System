from django.urls import path
from .views import (
    ConsultationListCreateView, ConsultationDetailView, ConsultationStartView,
    ConsultationCompleteView, ClinicalNoteCreateView, DiagnosisCreateView,
    PrescriptionCreateGetView, AIDecisionCreateView
)

urlpatterns = [
    path('consultations', ConsultationListCreateView.as_view(), name='consultation-list-create'),
    path('consultations/<uuid:consultation_id>', ConsultationDetailView.as_view(), name='consultation-detail'),
    path('consultations/<uuid:consultation_id>/start', ConsultationStartView.as_view(), name='consultation-start'),
    path('consultations/<uuid:consultation_id>/complete', ConsultationCompleteView.as_view(), name='consultation-complete'),
    path('consultations/<uuid:consultation_id>/notes', ClinicalNoteCreateView.as_view(), name='clinical-note-create'),
    path('consultations/<uuid:consultation_id>/diagnoses', DiagnosisCreateView.as_view(), name='diagnosis-create'),
    path('consultations/<uuid:consultation_id>/prescriptions', PrescriptionCreateGetView.as_view(), name='prescription-create-get'),
    path('consultations/<uuid:consultation_id>/ai-decisions', AIDecisionCreateView.as_view(), name='ai-decision-create'),
]
