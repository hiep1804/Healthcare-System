import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTUser:
    def __init__(self, payload):
        self.id = payload.get('user_id')
        self.payload = payload
        self.is_authenticated = True
        self.roles = payload.get('roles', [])

    def __str__(self):
        return f"JWTUser({self.id})"

    def has_role(self, role_name):
        return role_name in self.roles


class JWTServiceAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        token = auth_header[7:]
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"verify_exp": True},
            )
            user = JWTUser(payload)
            return (user, token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')
