from django.urls import path
from .views import InsurancePolicyListCreateView, EligibilityCheckView, ClaimListCreateView, ClaimDetailView, ClaimStatusView

urlpatterns = [
    path('insurance-policies', InsurancePolicyListCreateView.as_view(), name='policy-list-create'),
    path('insurance-policies/me', InsurancePolicyListCreateView.as_view(), name='policy-me'),
    path('eligibility-checks', EligibilityCheckView.as_view(), name='eligibility-check'),
    path('claims', ClaimListCreateView.as_view(), name='claim-list-create'),
    path('claims/<uuid:claim_id>', ClaimDetailView.as_view(), name='claim-detail'),
    path('claims/<uuid:claim_id>/status', ClaimStatusView.as_view(), name='claim-status'),
]
