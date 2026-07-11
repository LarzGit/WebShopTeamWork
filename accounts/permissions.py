from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.ADMIN
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Читання (GET/HEAD/OPTIONS) доступне будь-кому.
    Створення/редагування/видалення — тільки користувачам з роллю ADMIN.
    Використовується для керування каталогом (товари, категорії) згідно з ТЗ (п.4.6):
    керувати каталогом повинен лише адміністратор.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == request.user.Role.ADMIN
        )


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'user_id', None) == request.user.id