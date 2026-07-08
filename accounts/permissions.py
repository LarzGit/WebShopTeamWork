from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.ADMIN
        )


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'user_id', None) == request.user.id