from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Plan, PlanEntitlement, Subscription, SubscriptionUsage
from .serializers import (
    PlanSerializer, PlanEntitlementSerializer, SubscriptionSerializer,
    SubscriptionCreateSerializer, SubscriptionUsageSerializer
)
from common.permissions import IsAdmin, IsPatient, IsPatientOrAdmin


class PlanListCreateView(APIView):
    """
    GET /api/v1/plans - Public list of active plans (or all plans for Admin)
    POST /api/v1/plans - Create a new subscription plan (Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdmin()]
        return [AllowAny()]

    def get(self, request):
        show_all = request.query_params.get('all') == 'true' or (request.user and getattr(request.user, 'role', '') == 'ADMIN')
        if show_all:
            plans = Plan.objects.all()
        else:
            plans = Plan.objects.filter(is_active=True)
        serializer = PlanSerializer(plans, many=True)
        return Response({'data': serializer.data})

    def post(self, request):
        serializer = PlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        plan = serializer.save()

        # Handle entitlements if passed
        entitlements_data = request.data.get('entitlements', [])
        for ent in entitlements_data:
            ent_serializer = PlanEntitlementSerializer(data=ent)
            ent_serializer.is_valid(raise_exception=True)
            ent_serializer.save(plan=plan)

        return Response(PlanSerializer(plan).data, status=status.HTTP_201_CREATED)


class PlanDetailView(APIView):
    """
    PATCH /api/v1/plans/{plan_id} - Update plan details (Admin only)
    DELETE /api/v1/plans/{plan_id} - Deactivate/Delete plan (Admin only)
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, plan_id):
        try:
            plan = Plan.objects.get(id=plan_id)
        except Plan.DoesNotExist:
            return Response(
                {'error': {'code': 'PLAN_NOT_FOUND', 'message': 'Không tìm thấy gói dịch vụ.'}},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PlanSerializer(plan, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(PlanSerializer(plan).data)

    def delete(self, request, plan_id):
        try:
            plan = Plan.objects.get(id=plan_id)
            plan.is_active = False
            plan.save()
            return Response({'message': 'Đã vô hiệu hóa/hủy gói dịch vụ thành công.'})
        except Plan.DoesNotExist:
            return Response(
                {'error': {'code': 'PLAN_NOT_FOUND', 'message': 'Không tìm thấy gói dịch vụ.'}},
                status=status.HTTP_404_NOT_FOUND
            )


class SubscriptionListCreateView(APIView):
    """
    POST /api/v1/subscriptions - Subscribe to a plan (Patient only)
    GET /api/v1/subscriptions - View own or all subscriptions (Patient/Admin)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_role = getattr(request.user, 'role', '')
            if user_role == 'ADMIN':
                subscriptions = Subscription.objects.all()
                serializer = SubscriptionSerializer(subscriptions, many=True)
                return Response({'data': serializer.data})

            subscription = Subscription.objects.filter(patient_id=request.user.id, status='ACTIVE').first()
            if not subscription:
                return Response(
                    {'error': {'code': 'SUBSCRIPTION_NOT_FOUND', 'message': 'Bạn chưa đăng ký gói nào.'}},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(SubscriptionSerializer(subscription).data)
        except Exception as e:
            return Response({'error': {'code': 'ERROR', 'message': str(e)}}, status=400)

    def post(self, request):
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        plan = serializer.validated_data['plan']
        patient_id = serializer.validated_data['patient_id']

        # End any current active subscriptions
        Subscription.objects.filter(patient_id=patient_id, status='ACTIVE').update(status='EXPIRED')

        # Start dates based on billing cycle
        start_date = timezone.now()
        duration = timedelta(days=30) if plan.billing_cycle == 'MONTHLY' else timedelta(days=365)
        end_date = start_date + duration

        subscription = Subscription.objects.create(
            patient_id=patient_id,
            plan=plan,
            status='ACTIVE',
            current_period_start=start_date,
            current_period_end=end_date
        )

        # Create usage limits
        for ent in plan.entitlements.all():
            limit_val = 0
            try:
                limit_val = int(ent.value)
            except ValueError:
                pass  # for boolean values

            SubscriptionUsage.objects.create(
                subscription=subscription,
                entitlement=ent,
                usage_limit=limit_val,
                current_usage=0,
                reset_at=end_date
            )

        return Response(SubscriptionSerializer(subscription).data, status=status.HTTP_201_CREATED)


class SubscriptionCancelView(APIView):
    """PATCH/POST /api/v1/subscriptions/{subscription_id}/cancel - Cancel subscription (Patient/Admin)"""
    permission_classes = [IsAuthenticated, IsPatientOrAdmin]

    def patch(self, request, subscription_id):
        try:
            sub = Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            return Response(
                {'error': {'code': 'SUBSCRIPTION_NOT_FOUND', 'message': 'Không tìm thấy thông tin đăng ký.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        sub.cancel_at_period_end = True
        sub.status = 'CANCELLED'
        sub.save()
        return Response(SubscriptionSerializer(sub).data)

    def post(self, request, subscription_id):
        return self.patch(request, subscription_id)


class SubscriptionUsageView(APIView):
    """GET /api/v1/subscriptions/{subscription_id}/usage - View quotas and usage (Patient/Admin)"""
    permission_classes = [IsAuthenticated, IsPatientOrAdmin]

    def get(self, request, subscription_id):
        try:
            sub = Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            return Response(
                {'error': {'code': 'SUBSCRIPTION_NOT_FOUND', 'message': 'Không tìm thấy thông tin đăng ký.'}},
                status=status.HTTP_404_NOT_FOUND
            )

        usages = sub.usages.all()
        serializer = SubscriptionUsageSerializer(usages, many=True)
        return Response({'data': serializer.data})
