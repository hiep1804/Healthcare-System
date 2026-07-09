from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'has_role') and request.user.has_role('ADMIN')


class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'has_role') and request.user.has_role('DOCTOR')


class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'has_role') and request.user.has_role('PATIENT')


class IsProviderAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'has_role') and request.user.has_role('PROVIDER_ADMIN')


class IsDoctorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'has_role'):
            return False
        return request.user.has_role('DOCTOR') or request.user.has_role('ADMIN')


class IsPatientOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'has_role'):
            return False
        return request.user.has_role('PATIENT') or request.user.has_role('ADMIN')


class IsPatientOrDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'has_role'):
            return False
        return request.user.has_role('PATIENT') or request.user.has_role('DOCTOR')


class IsPatientOrDoctorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'has_role'):
            return False
        return (request.user.has_role('PATIENT') or request.user.has_role('DOCTOR') or request.user.has_role('ADMIN'))
