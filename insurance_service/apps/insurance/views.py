from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import InsurancePolicy, EligibilityCheck, Claim, ClaimItem
from .serializers import (
    InsurancePolicySerializer, EligibilityCheckSerializer, ClaimSerializer,
    ClaimCreateSerializer, EligibilityRequestSerializer, ClaimItemSerializer
)
from common.permissions import IsAdmin, IsPatient, IsPatientOrAdmin


class InsurancePolicyListCreateView(APIView):
    """
    POST /api/v1/insurance-policies - Add insurance policy (Patient/Admin)
    GET /api/v1/insurance-policies/me - View own policies (Patient only)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Mocks GET /api/v1/insurance-policies/me
        policies = InsurancePolicy.objects.filter(patient_id=request.user.id)
        serializer = InsurancePolicySerializer(policies, many=True)
        return Response({'data': serializer.data})

    def post(self, request):
        serializer = InsurancePolicySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        policy = serializer.save()
        return Response(InsurancePolicySerializer(policy).data, status=status.HTTP_201_CREATED)


class EligibilityCheckView(APIView):
    """POST /api/v1/eligibility-checks - Check policy eligibility (System/Admin)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EligibilityRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient_id = serializer.validated_data['patient_id']
        policy_number = serializer.validated_data['policy_number']
        provider_id = serializer.validated_data['provider_id']

        try:
            policy = InsurancePolicy.objects.get(policy_number=policy_number, patient_id=patient_id)
        except InsurancePolicy.DoesNotExist:
            return Response(
                {'error': {'code': 'POLICY_NOT_FOUND', 'message': 'Không tìm thấy thông tin bảo hiểm khớp với bệnh nhân.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        # Basic mock rules
        is_eligible = policy.status == 'ACTIVE' and policy.expiry_date >= timezone.now().date()
        status_val = 'ELIGIBLE' if is_eligible else 'NOT_ELIGIBLE'

        check = EligibilityCheck.objects.create(
            patient_id=patient_id,
            policy=policy,
            provider_id=provider_id,
            status=status_val,
            notes=f"Kiểm tra tự động. Hạn sử dụng: {policy.expiry_date}."
        )

        return Response(EligibilityCheckSerializer(check).data, status=status.HTTP_201_CREATED)


class ClaimListCreateView(APIView):
    """
    POST /api/v1/claims - Submit insurance claim (System/Admin)
    GET /api/v1/claims/{claim_id} - View claim details (Patient/Admin)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ClaimCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        claim = serializer.save()

        # Handle items if passed
        items_data = request.data.get('items', [])
        for item in items_data:
            item_serializer = ClaimItemSerializer(data=item)
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save(claim=claim)

        return Response(ClaimSerializer(claim).data, status=status.HTTP_201_CREATED)


class ClaimDetailView(APIView):
    """GET /api/v1/claims/{claim_id} - View claim details (Patient/Admin)"""
    permission_classes = [IsAuthenticated]

    def get(self, request, claim_id):
        try:
            claim = Claim.objects.get(id=claim_id)
        except Claim.DoesNotExist:
            return Response(
                {'error': {'code': 'CLAIM_NOT_FOUND', 'message': 'Không tìm thấy yêu cầu bồi thường.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ClaimSerializer(claim)
        return Response(serializer.data)


class ClaimStatusView(APIView):
    """PATCH /api/v1/claims/{claim_id}/status - Update claim status (Admin/System)"""
    permission_classes = [IsAuthenticated]

    def patch(self, request, claim_id):
        try:
            claim = Claim.objects.get(id=claim_id)
        except Claim.DoesNotExist:
            return Response(
                {'error': {'code': 'CLAIM_NOT_FOUND', 'message': 'Không tìm thấy yêu cầu bồi thường.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        new_status = request.data.get('status')
        if new_status not in ['APPROVED', 'REJECTED', 'PAID']:
            return Response(
                {'error': {'code': 'INVALID_STATUS', 'message': 'Trạng thái cập nhật không hợp lệ.'}},
                status=status.HTTP_400_BAD_REQUEST
            )

        claim.status = new_status
        claim.processed_at = timezone.now()
        claim.notes = request.data.get('notes', claim.notes)
        claim.save()

        return Response(ClaimSerializer(claim).data)
