from django.contrib import admin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import TokenProxy

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class IngredientAdmin(admin.ModelAdmin):
    """Настройки модели Ингридиент
    для отображения в панели администратора"""

    list_display = (
        'id',
        'name',
        'measurement_unit'
    )
    list_filter = ('name', )
    search_fields = ('name',)

    class Meta:
        ordering = ('name', )


class TagAdmin(admin.ModelAdmin):
    """Настройки модели Тэг
    для отображения в панели администратора"""

    list_display = (
        'id',
        'name',
        'slug'
    )


class IngredientRecipeInline(admin.TabularInline):
    model = Recipe.ingredients.through
    min_num = 1


class TagRecipeInline(admin.TabularInline):
    model = Recipe.tags.through
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    """Настройки модели Рецепт
    для отображения в панели администратора"""
    inlines = [
        IngredientRecipeInline,
        TagRecipeInline,
    ]
    list_display = (
        'name',
        'author',
        'tags_list',
        'ingredients_list',
        'count_favorite'
    )
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('count_favorite',)

    class Meta:
        ordering = ('-pub_date', )

    @admin.display(description='Ингридиенты')
    def ingredients_list(self, obj):
        """Получение ингридиентов рецепта."""
        return '\n'.join(
            (ingredient.name for ingredient in obj.ingredients.all())
        )

    @admin.display(description='Теги')
    def tags_list(self, obj):
        """Получение тегов рецепта."""
        return '\n'.join((tag.name for tag in obj.tags.all()))

    @admin.display(description='Добавили в избранное')
    def count_favorite(self, obj):
        """Показывает сколько раз рецепт добавлен в избранное."""
        return obj.favorites.count()


class FavoriteAdmin(admin.ModelAdmin):
    """Настройки модели Избранное
    для отображения в панели администратора"""

    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', )

    class Meta:
        ordering = ('user', )


class ShoppingCartAdmin(admin.ModelAdmin):
    """Настройки модели Список покупок
    для отображения в панели администратора"""

    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', )

    class Meta:
        ordering = ('user', )


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.unregister(Group)
admin.site.unregister(TokenProxy)
