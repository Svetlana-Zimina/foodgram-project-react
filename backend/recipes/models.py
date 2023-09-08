from colorfield.fields import ColorField
from django.core import validators
from django.db import models

from foodgram_backend import constants
from users.models import User


class Ingredient(models.Model):
    """Модель Ингредиенты."""

    name = models.CharField(
        max_length=constants.MAX_LENGTH_1,
        verbose_name='Название ингридиента'
    )
    measurement_unit = models.CharField(
        max_length=constants.MAX_LENGTH_1,
        verbose_name='Единицы измерения'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique ingredient measurement_unit'
            )]
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель Тэг."""

    name = models.CharField(
        max_length=constants.MAX_LENGTH_1,
        unique=True,
        verbose_name='Название тега'
    )
    color = ColorField(
        max_length=constants.MAX_LENGTH_2,
        unique=True,
        verbose_name='Цветовой HEX-код'
    )
    slug = models.SlugField(
        max_length=constants.MAX_LENGTH_1,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель Рецепт."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации'
    )
    name = models.CharField(
        max_length=constants.MAX_LENGTH_1,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Картинка'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
        help_text="Выберите ингредиенты."
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        related_name='recipes',
        verbose_name='Тэги',
        help_text="Выберите один или несколько тэгов."
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления блюда, мин.',
        validators=[
            validators.MinValueValidator(
                constants.MIN_VALUE,
                message=(
                    'Время приготовления должно быть не меньше',
                    f'{constants.MIN_VALUE}!'
                )
            ),
            validators.MaxValueValidator(
                constants.MAX_TIME_COOK,
                message=(
                    'Время приготовления не должно быть больше',
                    f'{constants.MAX_TIME_COOK}!'
                )
            ),
        ]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации рецепта'
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}, {self.author}'


class IngredientRecipe(models.Model):
    """Промежуточная модель Ингридиент - Рецепт."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        validators=[
            validators.MinValueValidator(
                constants.MIN_VALUE,
                message=(
                    'Количество ингридиента не может быть меньше',
                    f'{constants.MIN_VALUE}!'
                )
            ),
            validators.MaxValueValidator(
                constants.MAX_VALUE,
                message=(
                    'Количество ингридиента не может быть больше',
                    f'{constants.MAX_VALUE}!'
                )
            ),
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique ingredient'
            )]
        ordering = ('recipe', )
        verbose_name = 'ингредиент рецепта'
        verbose_name_plural = 'ингредиенты рецепта'

    def __str__(self):
        return f'{self.recipe}, {self.ingredient}'


class TagRecipe(models.Model):
    """Промежуточная модель Тэг - Рецепт."""

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tags'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_tags'
    )

    class Meta:
        ordering = ('tag', )
        verbose_name = 'тег рецепта'
        verbose_name_plural = 'теги рецепта'

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class CustomModel(models.Model):
    """Кастомная модель для наследования моделей Избранное и Список покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Выбранный рецепт'
    )

    class Meta:
        abstract = True
        ordering = ('user', )

    def __str__(self):
        return {self.user}, {self.recipe}


class Favorite(CustomModel):
    """Модель Избранное."""

    class Meta(CustomModel.Meta):
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            ),
        )


class ShoppingCart(CustomModel):
    """Модель Список покупок."""

    class Meta(CustomModel.Meta):
        verbose_name = 'Cписок покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe_in_shopping_cart'
            ),
        )
