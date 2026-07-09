from django.urls import path
from .views import (
    PatientCreateView, PatientMeView, PatientDetailView,
    AllergyListCreateView, ConditionListCreateView,
    MedicationListCreateView, ConsentCreateView, ConsentRevokeView,
)

urlpatterns = [
    path('patients', PatientCreateView.as_view(), name='patient-create'),
    path('patients/me', PatientMeView.as_view(), name='patient-me'),
    path('patients/<uuid:patient_id>', PatientDetailView.as_view(), name='patient-detail'),
    path('patients/<uuid:patient_id>/allergies', AllergyListCreateView.as_view(), name='patient-allergies'),
    path('patients/<uuid:patient_id>/conditions', ConditionListCreateView.as_view(), name='patient-conditions'),
    path('patients/<uuid:patient_id>/medications', MedicationListCreateView.as_view(), name='patient-medications'),
    path('patients/<uuid:patient_id>/consents', ConsentCreateView.as_view(), name='patient-consents'),
    path('patients/<uuid:patient_id>/consents/<uuid:consent_id>', ConsentRevokeView.as_view(), name='patient-consent-revoke'),
]
