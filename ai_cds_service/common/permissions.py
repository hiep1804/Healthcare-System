from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'has_role') and request.user.has_role('ADMIN')


class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'has_role') and request.user.has_role('DOCTOR')


class IsDoctorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not hasattr(request.user, 'has_role'):
            return False
        return request.user.has_role('DOCTOR') or request.user.has_role('ADMIN')
