from django.contrib import admin
from .models import User, Role, UserRole, Session, AuthFactor


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'status', 'is_mfa_enabled', 'created_at')
    list_filter = ('status', 'is_mfa_enabled')
    search_fields = ('email', 'username')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_at', 'assigned_by')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'ip_address', 'created_at', 'expires_at')
    list_filter = ('is_active',)


@admin.register(AuthFactor)
class AuthFactorAdmin(admin.ModelAdmin):
    list_display = ('user', 'factor_type', 'is_verified', 'created_at')
