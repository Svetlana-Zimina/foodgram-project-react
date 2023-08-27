import base64

from django.core.files.base import ContentFile
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag
)
from users.serializers import CustomUserSerializer


class Base64ImageField(serializers.ImageField):
    """Базовый класс сериализатора для добавления фото. Кодировка Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингридиентов в рецепте/списке рецептов."""

    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    def get_id(self, obj):
        """Получение id ингридиента."""
        return obj.ingredient.id

    def get_name(self, obj):
        """Получение названия ингридиента."""
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        """Получение единицы измерения ингридиента."""
        return obj.ingredient.measurement_unit

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientRecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингридиентов при создании рецепта."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = Ingredient
        fields = ('id', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe для вывода списка рецептов/рецепта."""

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_ingredients(self, obj):
        """Получение информации об ингридиентах рецепта."""
        ingredients = obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('ingredientrecipe__amount')
        )
        return ingredients

    def get_is_favorited(self, obj):
        """Получение информации находится ли рецепт в избранном."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Получение информации находится ли рецепт в
        списке покупок."""
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=user, recipe=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/редактирования/удаления рецепта."""

    author = CustomUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientRecipeShortSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, value):
        """Валидация поля ingredients."""
        if not value:
            raise ValidationError({
                'ingredients': 'Необходимо добавить ингрдиенты!'
            })
        ingredients_list = []
        for item in value:
            ingredient = get_object_or_404(Ingredient, id=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError({
                    'ingredients': 'Ингридиенты не могут повторяться!'
                })
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        """Валидация поля tags."""
        if not value:
            raise ValidationError({'tags': 'Необходимо добавить тег!'})
        tags_list = []
        for tag in value:
            if tag in tags_list:
                raise ValidationError({'tags': 'Теги не могуть повторяться!'})
            tags_list.append(tag)
        return value

    def create(self, validated_data):
        """Переопределение метода создания рецепта."""
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])

            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount
            )

        return recipe

    def update(self, instance, validated_data):
        """Переопределение метода редактирования рецепта."""
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.set(tags)

        ingredients = validated_data.pop('ingredients', None)
        if ingredients is not None:
            instance.ingredients.clear()

            for ingredient in ingredients:
                amount = ingredient['amount']
                ingredient = get_object_or_404(Ingredient, pk=ingredient['id'])

                IngredientRecipe.objects.update_or_create(
                    recipe=instance,
                    ingredient=ingredient,
                    defaults={'amount': amount}
                )

        return super().update(instance, validated_data)
