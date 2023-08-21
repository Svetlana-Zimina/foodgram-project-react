from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.serializers import RecipeShortSerializer
from users.models import Subscription, User


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]
        model = User

    def get_is_subscribed(self, obj):
        """Отметка подписан ли текущий пользователь на автора."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, following=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Кастомный сериализатор для создания Пользователя."""

    password = serializers.CharField(
        max_length=150, min_length=8, write_only=True)

    class Meta:
        fields = '__all__'
        model = User

    def validate(self, data):
        """Валидация имени и электронной почты нового пользователя."""
        if User.objects.filter(username=data.get('username')):
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует!'
            )
        if User.objects.filter(email=data.get('email')):
            raise serializers.ValidationError(
                'Пользователь с такой электронной почтой уже существует!'
            )
        return data


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для модели Подписки."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, object):
        """
        Получение рецептов автора,
        на которого подписан текущий пользователь.
        """
        author_recipes = object.recipes.all()[:6]
        return RecipeShortSerializer(
            author_recipes, many=True
        ).data

    def get_recipes_count(self, object):
        """
        Получение количества рецептов автора,
        на которого подписан текущий пользователь.
        """
        return object.recipes.count()

    def get_is_subscribed(self, obj):
        """Отметка подписан ли текущий пользователь на автора."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, following=obj).exists()
