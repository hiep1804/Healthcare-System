from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, RefreshTokenView,
    MFASetupView, MFAVerifyView,
    CurrentUserView, UserDetailView, UserStatusView, AssignRoleView, UserListView,
)

urlpatterns = [
    # Auth endpoints
    path('auth/register', RegisterView.as_view(), name='auth-register'),
    path('auth/login', LoginView.as_view(), name='auth-login'),
    path('auth/logout', LogoutView.as_view(), name='auth-logout'),
    path('auth/refresh-token', RefreshTokenView.as_view(), name='auth-refresh'),
    path('auth/mfa/setup', MFASetupView.as_view(), name='mfa-setup'),
    path('auth/mfa/verify', MFAVerifyView.as_view(), name='mfa-verify'),

    # User management endpoints
    path('users', UserListView.as_view(), name='user-list'),
    path('users/me', CurrentUserView.as_view(), name='user-me'),
    path('users/<uuid:user_id>', UserDetailView.as_view(), name='user-detail'),
    path('users/<uuid:user_id>/status', UserStatusView.as_view(), name='user-status'),
    path('users/<uuid:user_id>/roles', AssignRoleView.as_view(), name='user-assign-role'),
]
