from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Recipe
from .models import Subscription, User


class CustomUserSerializer(UserSerializer):
    """Кастомный сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        """Отметка подписан ли текущий пользователь на автора."""
        user = self.context['request'].user
        if user and user.is_authenticated:
            return user.following.filter(user=obj).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения информации о рецепте в подписке."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class SubscriptionSerializer(CustomUserSerializer):
    """Сериализатор для отображения модели Подписки."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        model = User
        fields = CustomUserSerializer.Meta.fields + [
            'recipes',
            'recipes_count'
        ]

    def get_recipes(self, obj):
        """
        Получение рецептов автора,
        на которого подписан текущий пользователь.
        """
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except TypeError:
                return ('В параметр limit нужно передать целое число.',
                        f'Передано: {type(limit)}')
        return RecipeShortSerializer(recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        """
        Получение количества рецептов автора,
        на которого подписан текущий пользователь.
        """
        return obj.recipes.count()


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/удаления Подписки."""

    class Meta():
        model = Subscription
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписались на этого автора!'
            )
        ]

    def validate(self, data):
        """Проверка, что пользователь не подписывается на самого себя."""
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return data
