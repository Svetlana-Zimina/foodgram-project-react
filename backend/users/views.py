from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .models import User, Subscription

from .permissions import (
    AdminOnly,
    IsAdminOrReadOnly,
)
from .serializers import (
    SubscriptionSerializer,
    SignUpSerializer,
    TokenSerializer,
    UserInfoSerializer,
    UserSerializer,
)

class CreateListViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Кастомный ViewSet: создание и получение списка."""
    pass


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try:
        user = serializer.save()
    except ValidationError as e:
        return Response(
            {"description": str(e)},
            status=400,
        )

    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject="Yamdb SignUp",
        message=f"feel free to use this confirmation code {confirmation_code}",
        from_email=None,
        recipient_list=[
            user.email,
        ],
    )

    return Response(serializer.data, status=200)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def obtain_token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"],
    )
    if not default_token_generator.check_token(
        user, serializer.validated_data["confirmation_code"]
    ):
        return Response(
            {"description": "wrong confirmation code"},
            status=400,
        )
    token = AccessToken.for_user(user)
    return Response(
        {"token": str(token)},
        status=200,
    )


class UserViewSet(viewsets.ModelViewSet):
    lookup_field = "username"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        AdminOnly,
    ]
    search_fields = ("username",)
    filter_backends = (SearchFilter,)
    http_method_names = ["get", "post", "patch", "delete"]

    @action(
        methods=[
            "get",
            "patch",
        ],
        detail=False,
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
        serializer_class=UserInfoSerializer,
    )
    def user_profile(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=200)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(status=405)


class SubscriptionViewSet(CreateListViewSet):
    """Представление для модели Subscription."""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    #permission_classes = (permissions.IsAuthenticated,)
    #filter_backends = (filters.SearchFilter,)
    #search_fields = ('following__username',)

    def get_queryset(self):
        """
        Получение пользователя из эндпоинта.
        """
        return self.request.user.follower

    def perform_create(self, serializer):
        """
        Автоматическое указание пользователя, создавшего подписку.
        """
        serializer.save(user=self.request.user)