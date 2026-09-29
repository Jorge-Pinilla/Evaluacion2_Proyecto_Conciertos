# api/permissions.py
from rest_framework import permissions

class EspectadorOnly(permissions.BasePermission):
    """Permiso exclusivo para usuarios con rol ESPECTADOR."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ESPECTADOR'

class OrganizadorOnly(permissions.BasePermission):
    """Permiso exclusivo para usuarios con rol ORGANIZADOR."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ORGANIZADOR'