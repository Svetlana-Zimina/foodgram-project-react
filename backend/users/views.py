from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import exceptions, status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from recipes.permissions import IsAuthorPermission

from .models import Subscription, User
from .serializers import (
    CustomUserSerializer,
    SubscriptionSerializer
)


class CustomUserViewSet(UserViewSet):
    """Представление для кастомной модели Пользователя."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @action(
        detail=False,
        methods=['get', ],
        permission_classes=(IsAuthenticated,)
    )
    def get_me(self, request):
        """Получение информации о текущем пользователе."""
        serializer = CustomUserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=('get',),
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthorPermission, )
    )
    def subscriptions(self, request):
        """Получение всех подписок текущего пользователя."""
        user = self.request.user

        def queryset():
            return User.objects.filter(following__user=user)

        self.get_queryset = queryset
        return self.list(request)

    @action(
        detail=True,
        methods=('post', 'delete'),
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, id=None):
        """Подписка/отписка от автора."""
        user = self.request.user
        following = get_object_or_404(User, id=id)

        if self.request.method == 'POST':
            if Subscription.objects.filter(
                user=user,
                following=following
            ).exists():
                raise exceptions.ValidationError(
                    'Вы уже подписаны на этого автора!'
                )
            Subscription.objects.create(user=user, following=following)
            serializer = SubscriptionSerializer(
                following,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=user,
                following=following
            ).exists():
                raise exceptions.ValidationError(
                    'Невозможно удалить то, чего нет.'
                )
            subscription = get_object_or_404(
                Subscription,
                user=user,
                following=following
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
