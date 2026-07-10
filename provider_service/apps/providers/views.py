from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Specialty, Clinic, Provider, DoctorLicense, ProviderService
from .serializers import (
    SpecialtySerializer, ClinicSerializer, DoctorLicenseSerializer,
    ProviderServiceSerializer, ProviderSerializer, ProviderCreateSerializer,
    VerificationSerializer
)
from common.permissions import IsDoctor, IsAdmin, IsDoctorOrAdmin


class SpecialtyListCreateView(APIView):
    """
    GET /api/v1/specialties - Public list of specialties
    POST /api/v1/specialties - Create specialty (Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdmin()]
        return [AllowAny()]

    def get(self, request):
        specialties = Specialty.objects.all()
        serializer = SpecialtySerializer(specialties, many=True)
        return Response({'data': serializer.data})

    def post(self, request):
        serializer = SpecialtySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        specialty = serializer.save()
        return Response(SpecialtySerializer(specialty).data, status=status.HTTP_201_CREATED)


class ProviderMeView(APIView):
    """
    GET /api/v1/providers/me - View own provider profile (Doctor)
    PATCH /api/v1/providers/me - Update own provider profile (Doctor)
    """
    permission_classes = [IsAuthenticated, IsDoctor]

    def get(self, request):
        try:
            provider = Provider.objects.get(user_id=request.user.id)
        except Provider.DoesNotExist:
            return Response(
                {'error': {'code': 'PROVIDER_NOT_FOUND', 'message': 'Hồ sơ bác sĩ chưa được tạo.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProviderSerializer(provider)
        return Response(serializer.data)

    def patch(self, request):
        try:
            provider = Provider.objects.get(user_id=request.user.id)
        except Provider.DoesNotExist:
            return Response(
                {'error': {'code': 'PROVIDER_NOT_FOUND', 'message': 'Hồ sơ bác sĩ chưa được tạo.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProviderCreateSerializer(provider, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProviderSerializer(provider).data)


class ProviderListCreateView(APIView):
    """
    GET /api/v1/providers - Search and list providers (Public)
    POST /api/v1/providers - Create provider profile (Doctor/Admin)
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsDoctorOrAdmin()]
        return [AllowAny()]

    def get(self, request):
        queryset = Provider.objects.filter(status='VERIFIED')

        # Filter by specialty_id (UUID or name matches provider's services)
        specialty_id = request.query_params.get('specialty_id')
        if specialty_id:
            queryset = queryset.filter(services__specialty_id=specialty_id).distinct()

        # Filter by location
        location = request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by price range
        min_price = request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(services__price__gte=min_price).distinct()

        max_price = request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(services__price__lte=max_price).distinct()

        # In MVP, available_date filtering can be mocked or basic
        # In full design, it joins with appointment-service time slots
        # For now, we will return the matching providers.

        # Apply standard pagination manually since we're using APIView
        from common.pagination import StandardResultsSetPagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = ProviderSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ProviderSerializer(queryset, many=True)
        return Response({'data': serializer.data})

    def post(self, request):
        serializer = ProviderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.save()
        return Response(ProviderSerializer(provider).data, status=status.HTTP_201_CREATED)


class ProviderDetailView(APIView):
    """
    GET /api/v1/providers/{provider_id} - View provider details (Public)
    PATCH /api/v1/providers/{provider_id} - Update provider details (Doctor/Admin)
    """
    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthenticated(), IsDoctorOrAdmin()]
        return [AllowAny()]

    def get(self, request, provider_id):
        try:
            provider = Provider.objects.get(id=provider_id)
        except Provider.DoesNotExist:
            return Response(
                {'error': {'code': 'PROVIDER_NOT_FOUND', 'message': 'Không tìm thấy bác sĩ.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProviderSerializer(provider)
        return Response(serializer.data)

    def patch(self, request, provider_id):
        try:
            provider = Provider.objects.get(id=provider_id)
        except Provider.DoesNotExist:
            return Response(
                {'error': {'code': 'PROVIDER_NOT_FOUND', 'message': 'Không tìm thấy bác sĩ.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProviderCreateSerializer(provider, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProviderSerializer(provider).data)


class LicenseUploadView(APIView):
    """POST /api/v1/providers/{provider_id}/licenses - Upload license document (Doctor/Admin)"""
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def post(self, request, provider_id):
        try:
            provider = Provider.objects.get(id=provider_id)
        except Provider.DoesNotExist:
            return Response(
                {'error': {'code': 'PROVIDER_NOT_FOUND', 'message': 'Không tìm thấy bác sĩ.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = DoctorLicenseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        license = serializer.save(provider=provider)
        return Response(DoctorLicenseSerializer(license).data, status=status.HTTP_201_CREATED)


class ProviderVerificationView(APIView):
    """PATCH /api/v1/providers/{provider_id}/verification - Verify provider profile (Admin only)"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, provider_id):
        try:
            provider = Provider.objects.get(id=provider_id)
        except Provider.DoesNotExist:
            return Response(
                {'error': {'code': 'PROVIDER_NOT_FOUND', 'message': 'Không tìm thấy bác sĩ.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = VerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider.status = serializer.validated_data['status']
        provider.verification_notes = serializer.validated_data.get('notes', '')
        provider.save()
        return Response(ProviderSerializer(provider).data)


class ProviderServiceListCreateView(APIView):
    """POST /api/v1/providers/{provider_id}/services - Create service (Doctor/Admin)"""
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def post(self, request, provider_id):
        try:
            provider = Provider.objects.get(id=provider_id)
        except Provider.DoesNotExist:
            return Response(
                {'error': {'code': 'PROVIDER_NOT_FOUND', 'message': 'Không tìm thấy bác sĩ.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProviderServiceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prov_service = serializer.save(provider=provider)
        return Response(ProviderServiceSerializer(prov_service).data, status=status.HTTP_201_CREATED)


class ProviderServiceDetailView(APIView):
    """PATCH /api/v1/providers/{provider_id}/services/{service_id} - Update service price/duration (Doctor/Admin)"""
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def patch(self, request, provider_id, service_id):
        try:
            prov_service = ProviderService.objects.get(id=service_id, provider_id=provider_id)
        except ProviderService.DoesNotExist:
            return Response(
                {'error': {'code': 'SERVICE_NOT_FOUND', 'message': 'Không tìm thấy dịch vụ.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ProviderServiceSerializer(prov_service, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ProviderServiceSerializer(prov_service).data)
