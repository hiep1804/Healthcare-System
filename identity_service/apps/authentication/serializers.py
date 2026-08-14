from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Role, UserRole, AuthFactor


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration."""
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    role = serializers.ChoiceField(
        choices=['PATIENT', 'DOCTOR'],
        default='PATIENT',
        help_text='Only PATIENT and DOCTOR can self-register'
    )

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("email đã tồn tại")
        return value

    def validate_phone(self, value):
        if value and User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("số điện thoại đã tồn tại")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username đã được sử dụng.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Mật khẩu không khớp."})
        return attrs

    def create(self, validated_data):
        role_name = validated_data.pop('role', 'PATIENT')
        validated_data.pop('password_confirm')
        phone = validated_data.get('phone')
        if not phone:
            phone = None
            
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=phone,
        )
        # Assign role
        role, _ = Role.objects.get_or_create(name=role_name)
        UserRole.objects.create(user=user, role=role)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField(help_text='Email or username')
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Try email first, then username
        user = authenticate(username=username, password=password)
        if user is None:
            # Try by email
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is None:
            raise serializers.ValidationError("Email/username hoặc mật khẩu không đúng.")

        if user.status != 'ACTIVE':
            raise serializers.ValidationError("Tài khoản đã bị khóa.")

        attrs['user'] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    roles = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'phone', 'status',
            'is_mfa_enabled', 'roles', 'role', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'email', 'created_at', 'updated_at']

    def get_roles(self, obj):
        roles = list(obj.user_roles.values_list('role__name', flat=True))
        roles.sort(key=lambda r: {'ADMIN': 1, 'DOCTOR': 2, 'PROVIDER_ADMIN': 3, 'PATIENT': 4}.get(r, 99))
        return roles

    def get_role(self, obj):
        roles = self.get_roles(obj)
        return roles[0] if roles else None


class UserStatusSerializer(serializers.Serializer):
    """Serializer for updating user status."""
    status = serializers.ChoiceField(choices=['ACTIVE', 'INACTIVE', 'SUSPENDED'])
    reason = serializers.CharField(required=False, allow_blank=True)


class AssignRoleSerializer(serializers.Serializer):
    """Serializer for assigning a role to a user."""
    role = serializers.ChoiceField(choices=['PATIENT', 'DOCTOR', 'ADMIN', 'PROVIDER_ADMIN'])


class MFASetupSerializer(serializers.Serializer):
    """Response serializer for MFA setup."""
    secret = serializers.CharField(read_only=True)
    qr_uri = serializers.CharField(read_only=True)


class MFAVerifySerializer(serializers.Serializer):
    """Serializer for MFA verification."""
    code = serializers.CharField(max_length=6, min_length=6)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at']
