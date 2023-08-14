from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination

from recipes.models import (
    Recipe,
    Ingredient,
    Tag,
    Favorite,
    User
)
#from .permissions import IsAuthorOrReadOnly
from .serializers import (
    RecipeSerializer,
    IngredientSerializer,
    TagSerializer,
    FavoriteSerializer
)


class CreateListViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Кастомный ViewSet: создание и получение списка."""
    pass


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление для модели Recipe."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    #permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        """Автоматическое указание автора при создании рецепта."""

        serializer.save(author=self.request.user)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Представление для модели Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    #permission_classes = (permissions.AllowAny,)


class TagViewSet(viewsets.ModelViewSet):
    """Представление для модели Tag."""

    serializer_class = TagSerializer
    #permission_classes = (IsAuthorOrReadOnly,)


class FavoriteViewSet(CreateListViewSet):
    """Представление для модели Favorite."""

    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    #permission_classes = (permissions.IsAuthenticated,)
    #filter_backends = (filters.SearchFilter,)
    #search_fields = ('following__username',)
