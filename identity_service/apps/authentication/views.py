from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import pyotp

from .models import User, Role, UserRole, Session, AuthFactor
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    UserStatusSerializer, AssignRoleSerializer,
    MFASetupSerializer, MFAVerifySerializer,
)
from .permissions import IsAdmin, IsDoctorOrAdmin


class RegisterView(APIView):
    """POST /api/v1/auth/register - Register new patient or doctor account."""
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # Security: Only admins can register non-patient roles
        if data.get('role') and data.get('role') != 'PATIENT':
            if not request.user.is_authenticated or not request.user.user_roles.filter(role__name='ADMIN').exists():
                return Response({"error": "Chỉ Admin mới có quyền tạo tài khoản Bác sĩ."}, status=status.HTTP_403_FORBIDDEN)

        serializer = RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = RefreshToken.for_user(user)
        roles = list(user.user_roles.values_list('role__name', flat=True))
        tokens['roles'] = roles
        access_token = tokens.access_token
        access_token['roles'] = roles
        return Response({
            'access_token': str(access_token),
            'refresh_token': str(tokens),
            'expires_in': 3600,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'last_name': user.last_name,
                'role': roles[0] if roles else None,
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """POST /api/v1/auth/login - User login."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Check if MFA is enabled
        if user.is_mfa_enabled:
            return Response({
                'mfa_required': True,
                'user_id': str(user.id),
                'message': 'Vui lòng xác minh MFA.',
            }, status=status.HTTP_200_OK)

        tokens = RefreshToken.for_user(user)
        roles = list(user.user_roles.values_list('role__name', flat=True))
        tokens['roles'] = roles
        access_token = tokens.access_token
        access_token['roles'] = roles

        # Create session
        Session.objects.create(
            user=user,
            refresh_token_jti=str(tokens['jti']),
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=timezone.now() + timedelta(days=7),
        )

        return Response({
            'access_token': str(access_token),
            'refresh_token': str(tokens),
            'expires_in': 3600,
            'user': {
                'id': str(user.id),
                'email': user.email,
                'last_name': user.last_name,
                'role': roles[0] if roles else None,
            }
        })

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')


class LogoutView(APIView):
    """POST /api/v1/auth/logout - User logout."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                # Deactivate session
                Session.objects.filter(
                    refresh_token_jti=str(token['jti'])
                ).update(is_active=False)
        except Exception:
            pass
        return Response({'message': 'Đăng xuất thành công.'}, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    """POST /api/v1/auth/refresh-token - Refresh access token."""
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response(
                {'error': {'code': 'MISSING_REFRESH_TOKEN', 'message': 'Refresh token is required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            return Response({
                'access_token': str(token.access_token),
                'refresh_token': str(token),
                'expires_in': 3600,
            })
        except Exception:
            return Response(
                {'error': {'code': 'INVALID_TOKEN', 'message': 'Token không hợp lệ hoặc đã hết hạn.'}},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class MFASetupView(APIView):
    """POST /api/v1/auth/mfa/setup - Setup MFA for doctor/admin."""
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def post(self, request):
        user = request.user
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name='Healthcare Marketplace'
        )

        AuthFactor.objects.update_or_create(
            user=user,
            factor_type='TOTP',
            defaults={'secret': secret, 'is_verified': False}
        )

        return Response({
            'secret': secret,
            'qr_uri': provisioning_uri,
            'message': 'Quét mã QR bằng ứng dụng Authenticator và xác minh bằng mã OTP.',
        })


class MFAVerifyView(APIView):
    """POST /api/v1/auth/mfa/verify - Verify MFA code."""
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get('user_id')
        code = request.data.get('code')

        if not user_id or not code:
            return Response(
                {'error': {'code': 'MISSING_FIELDS', 'message': 'user_id and code are required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id)
            auth_factor = AuthFactor.objects.get(user=user, factor_type='TOTP')
        except (User.DoesNotExist, AuthFactor.DoesNotExist):
            return Response(
                {'error': {'code': 'MFA_NOT_SETUP', 'message': 'MFA chưa được thiết lập.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        totp = pyotp.TOTP(auth_factor.secret)
        if totp.verify(code):
            if not auth_factor.is_verified:
                auth_factor.is_verified = True
                auth_factor.save()
                user.is_mfa_enabled = True
                user.save()

            tokens = RefreshToken.for_user(user)
            roles = list(user.user_roles.values_list('role__name', flat=True))
            tokens['roles'] = roles
            access_token = tokens.access_token
            access_token['roles'] = roles
            roles = list(user.user_roles.values_list('role__name', flat=True))

            Session.objects.create(
                user=user,
                refresh_token_jti=str(tokens['jti']),
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                expires_at=timezone.now() + timedelta(days=7),
            )

            return Response({
                'access_token': str(access_token),
                'refresh_token': str(tokens),
                'expires_in': 3600,
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'last_name': user.last_name,
                    'role': roles[0] if roles else None,
                }
            })
        else:
            return Response(
                {'error': {'code': 'INVALID_MFA_CODE', 'message': 'Mã OTP không hợp lệ.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CurrentUserView(APIView):
    """
    GET /api/v1/users/me - Get current user info.
    PATCH /api/v1/users/me - Update current user info.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserDetailView(APIView):
    """GET /api/v1/users/{user_id} - View user by ID (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': {'code': 'USER_NOT_FOUND', 'message': 'User không tồn tại.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserStatusView(APIView):
    """PATCH /api/v1/users/{user_id}/status - Lock/unlock user (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': {'code': 'USER_NOT_FOUND', 'message': 'User không tồn tại.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = UserStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.status = serializer.validated_data['status']
        user.save()
        return Response(UserSerializer(user).data)


class AssignRoleView(APIView):
    """POST /api/v1/users/{user_id}/roles - Assign role to user (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': {'code': 'USER_NOT_FOUND', 'message': 'User không tồn tại.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_name = serializer.validated_data['role']
        role, _ = Role.objects.get_or_create(name=role_name)

        user_role, created = UserRole.objects.get_or_create(
            user=user, role=role,
            defaults={'assigned_by': request.user}
        )

        if not created:
            return Response(
                {'error': {'code': 'ROLE_ALREADY_ASSIGNED', 'message': 'Role đã được gán trước đó.'}},
                status=status.HTTP_409_CONFLICT,
            )

        return Response({
            'message': f'Đã gán role {role_name} cho {user.email}.',
            'user': UserSerializer(user).data,
        }, status=status.HTTP_201_CREATED)
