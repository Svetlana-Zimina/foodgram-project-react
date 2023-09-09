from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.pagination import CustomPagination
from recipes.permissions import IsAuthorPermission
from .models import Subscription, User
from .serializers import (CustomUserSerializer, SubscriptionCreateSerializer,
                          SubscriptionSerializer)


class CustomUserViewSet(UserViewSet):
    """Представление для кастомной модели Пользователя."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    @action(
        detail=False,
        methods=('get',),
        serializer_class=SubscriptionSerializer,
        permission_classes=(IsAuthorPermission, )
    )
    def subscriptions(self, request):
        """Получение всех подписок текущего пользователя."""
        user = self.request.user
        queryset = User.objects.filter(following__user=user)
        paginator = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            paginator,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    # SubscriptionCreateSerializer основан на модели Subscription,
    # SubscriptionSerializer основан на модели User - для отображения
    # подписок согласно документации
    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """Подписка на автора."""
        following = get_object_or_404(User, id=id)
        data = {'user': request.user.id, 'following': following.id}
        serializer = SubscriptionCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = SubscriptionSerializer(
            following,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Отписка от автора."""
        following = get_object_or_404(User, id=id)
        delete_cnt, _ = Subscription.objects.filter(
            user=request.user,
            following=following
        ).delete()
        if not delete_cnt:
            return Response(
                {'ValidationError': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)
