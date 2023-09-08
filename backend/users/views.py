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

    @staticmethod
    def custom_create(serializer_create, serializer_show, pk, request):
        following = get_object_or_404(User, id=pk)
        data = {'user': request.user.id, 'following': following.id}
        serializer = serializer_create(data=data)
        if serializer.is_valid():
            serializer.save()
            serializer_show = serializer_show(
                following, context={'request': request}
            )
            return Response(
                serializer_show.data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """Подписка/отписка от автора."""
        return self.custom_create(
            SubscriptionCreateSerializer,
            SubscriptionSerializer,
            id,
            request
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """Удаление рецепта из избранного."""
        following = get_object_or_404(User, id=id)
        if Subscription.objects.filter(
            user=request.user,
            following=following
        ).exists():
            Subscription.objects.filter(
                user=request.user,
                following=following
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )
