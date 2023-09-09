from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.serializers import RecipeShortSerializer
from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)
from .pagination import CustomPagination
from .permissions import (AdminOrReadOnly, AuthorAdminOrReadOnly,
                          IsAuthorPermission)
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для модели Recipe.

    Получение списка рецептов/рецепта.
    Добавление/удаление рецепта из избранного.
    Добавление/удаление рецепта в список покупок.
    """

    queryset = Recipe.objects.all()
    permission_classes = (AuthorAdminOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Выбор сериализатора."""
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # FavoriteSerializer/ShoppingCartSerializer основаны на моделях
    # Favorite/ ShoppingCart,
    # RecipeShortSerializer основан на модели Recipe - для отображения
    # рецептов в избранном/ списке покупок согласно документации
    @staticmethod
    def custom_create(serializer_create, serializer_show, pk, request):
        recipe = get_object_or_404(Recipe, id=pk)
        data = {'user': request.user.id, 'recipe': recipe.id}
        serializer = serializer_create(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = serializer_show(
            recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(IsAuthorPermission,)
    )
    def favorite(self, request, pk):
        """Добавление рецепта в избранное."""
        return self.custom_create(
            FavoriteSerializer,
            RecipeShortSerializer,
            pk,
            request
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        """Удаление рецепта из избранного."""
        recipe = get_object_or_404(Recipe, id=pk)
        delete_cnt, _ = Favorite.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        if not delete_cnt:
            return Response(
                {'ValidationError': 'Этого рецепта нет в избранном'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', ),
        permission_classes=(IsAuthorPermission, )
    )
    def shopping_cart(self, request, pk):
        """Добавление рецепта в список покупок."""
        return self.custom_create(
            ShoppingCartSerializer,
            RecipeShortSerializer,
            pk,
            request
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        """Удаление рецепта из из списка покупок."""
        recipe = get_object_or_404(Recipe, id=pk)
        delete_cnt, _ = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).delete()
        if not delete_cnt:
            return Response(
                {'ValidationError': 'Этого рецепта нет в списке покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def save_file(list_for_print):
        """Сохранение списка покупок в файл."""
        list_name = 'Список покупок.'
        for item in list_for_print:
            ingredient = Ingredient.objects.get(pk=item['ingredient'])
            amount = item['amount']
            list_name += (
                f'{ingredient.name}, {amount} '
                f'{ingredient.measurement_unit}\n'
            )
        response = HttpResponse(list_name, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename=shopping_list.txt'
        )
        return response

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthorPermission, )
    )
    def download_shopping_cart(self, request):
        """Скачать список покупок."""
        shopping_cart = ShoppingCart.objects.filter(user=self.request.user)
        recipes = [item.recipe.id for item in shopping_cart]
        shopping_list = IngredientRecipe.objects.filter(
            recipe__in=recipes
        ).values(
            'ingredient'
        ).annotate(
            amount=Sum('amount')
        )
        return self.save_file(shopping_list)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для модели Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly, )
    pagination_class = None
