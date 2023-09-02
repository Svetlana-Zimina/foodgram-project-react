from rest_framework import permissions


class AuthorAdminOrReadOnly(permissions.BasePermission):
    """
    Кастомное разрешение.

    Без аутентификации возможны только безопасные методы.
    Только автор или админ может изменять свой контент.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
        )


class IsAuthorPermission(permissions.BasePermission):
    """
    Кастомное разрешение.

    Только автор может добавлять/удалять что-то в список
    покупок, избранные рецепты и подписываться/отписываться
    от пользователей.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class AdminOrReadOnly(permissions.BasePermission):
    """
    Кастомное разрешение.

    Действие может выполнять только админ.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
        )
