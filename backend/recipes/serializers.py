from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from foodgram_backend import constants
from users.serializers import CustomUserSerializer
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)


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

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class IngredientRecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингридиентов при создании рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient',
    )
    amount = serializers.IntegerField(
        max_value=constants.MAX_INGREDIENT_VALUE,
        min_value=constants.MIN_INGREDIENT_VALUE
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount',)


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe для вывода списка рецептов/рецепта."""

    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True,
        source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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

    def get_is_favorited(self, obj):
        """Получение информации находится ли рецепт в избранном."""
        request = self.context['request']
        return bool(
            request
            and request.user.is_authenticated
            and request.user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Получение информации находится ли рецепт в
        списке покупок."""
        request = self.context['request']
        return bool(
            request
            and request.user.is_authenticated
            and request.user.shopping_cart.filter(recipe=obj).exists()
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/редактирования/удаления рецепта."""

    author = CustomUserSerializer(read_only=True,)
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

    def validate(self, data):
        """Валидация полей Ингридиент и Тег."""
        if not data.get('ingredients'):
            raise ValidationError(
                'Необходимо добавить ингридиенты!'
            )
        elif not data.get('tags'):
            raise ValidationError('Необходимо добавить тег!')
        elif not data.get('image'):
            raise ValidationError('Необходимо добавить фото!')

        ingredients_list = [item['ingredient'].id
                            for item in data['ingredients']]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                'Ингридиенты не могут повторяться!'
            )

        tags = [item.id for item in data['tags']]
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги не могут повторяться!'
            )
        return data

    @staticmethod
    def add_ingredients(recipe, ingredients):
        """Добавление ингредиентов в рецепт."""
        IngredientRecipe.objects.bulk_create(
            IngredientRecipe(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients)

    def create(self, validated_data):
        """Переопределение метода создания рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        """Переопределение метода редактирования рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        IngredientRecipe.objects.filter(recipe=instance).delete()

        instance.tags.set(tags)
        self.add_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeListSerializer(
            instance,
            context={'request': self.context.get('request')}
        )

        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Избранное."""

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже добавлен в избранное'
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingCart."""

    class Meta:
        model = ShoppingCart
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Этот рецепт уже добавлен в список покупок'
            )
        ]
