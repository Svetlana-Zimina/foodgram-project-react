from rest_framework import permissions


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


class AuthorAdminOrReadOnly(permissions.BasePermission):
    """
    Кастомное разрешение.

    Только автор или админ могут менять или удалять свой контент.
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
