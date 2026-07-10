from django.urls import path
from .views import (
    SpecialtyListCreateView, ProviderListCreateView, ProviderDetailView, ProviderMeView,
    LicenseUploadView, ProviderVerificationView, ProviderServiceListCreateView,
    ProviderServiceDetailView
)

urlpatterns = [
    path('specialties', SpecialtyListCreateView.as_view(), name='specialty-list-create'),
    path('providers', ProviderListCreateView.as_view(), name='provider-list-create'),
    path('providers/me', ProviderMeView.as_view(), name='provider-me'),
    path('providers/<uuid:provider_id>', ProviderDetailView.as_view(), name='provider-detail'),
    path('providers/<uuid:provider_id>/licenses', LicenseUploadView.as_view(), name='license-upload'),
    path('providers/<uuid:provider_id>/verification', ProviderVerificationView.as_view(), name='provider-verify'),
    path('providers/<uuid:provider_id>/services', ProviderServiceListCreateView.as_view(), name='provider-service-list-create'),
    path('providers/<uuid:provider_id>/services/<uuid:service_id>', ProviderServiceDetailView.as_view(), name='provider-service-detail'),
]
