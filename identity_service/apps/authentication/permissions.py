from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access only to Admin users."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.user_roles.filter(role__name='ADMIN').exists()


class IsDoctor(permissions.BasePermission):
    """Allow access only to Doctor users."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.user_roles.filter(role__name='DOCTOR').exists()


class IsPatient(permissions.BasePermission):
    """Allow access only to Patient users."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.user_roles.filter(role__name='PATIENT').exists()


class IsProviderAdmin(permissions.BasePermission):
    """Allow access only to Provider Admin users."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.user_roles.filter(role__name='PROVIDER_ADMIN').exists()


class IsDoctorOrAdmin(permissions.BasePermission):
    """Allow access to Doctor or Admin."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.user_roles.filter(
            role__name__in=['DOCTOR', 'ADMIN']
        ).exists()


class IsPatientOrAdmin(permissions.BasePermission):
    """Allow access to Patient or Admin."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.user_roles.filter(
            role__name__in=['PATIENT', 'ADMIN']
        ).exists()


class IsPatientOrDoctor(permissions.BasePermission):
    """Allow access to Patient or Doctor."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.user_roles.filter(
            role__name__in=['PATIENT', 'DOCTOR']
        ).exists()


class IsPatientOrDoctorOrAdmin(permissions.BasePermission):
    """Allow access to Patient, Doctor or Admin."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.user_roles.filter(
            role__name__in=['PATIENT', 'DOCTOR', 'ADMIN']
        ).exists()
