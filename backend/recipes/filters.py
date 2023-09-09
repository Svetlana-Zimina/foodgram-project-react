from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from .models import Ingredient, Recipe

User = get_user_model()


class RecipeFilter(filters.FilterSet):
    """Кастомный фильтр для рецептов."""

    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        lookup_expr='contains'
    )

    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author']

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация по отметке "в избранном"."""
        user = self.request.user
        if value:
            return queryset.filter(favorites__user_id=user.pk)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация по отметке "в списке покупок"."""
        user = self.request.user
        if value:
            return queryset.filter(shopping_cart__user_id=user.pk)
        return queryset


class IngredientFilter(filters.FilterSet):
    """Кастомный фильтр для Ингридиентов."""

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']
