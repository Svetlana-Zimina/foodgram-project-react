import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    Favorite,
    User
)


class Base64ImageField(serializers.ImageField):
    """Базовый класс сериализатора для добавления фото. Кодировка Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )
    image = Base64ImageField()

    class Meta:
        exclude = ('pub_date',)
        model = Recipe


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        fields = '__all__'
        model = Ingredient
        

class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        fields = '__all__'
        model = Tag


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Favorite."""
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    favorite_recipe = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='recipes'
    )

    class Meta:
        fields = ('user', 'favorite_recipe')
        model = Favorite
