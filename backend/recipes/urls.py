from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import (
    RecipeViewSet,
    IngredientViewSet,
    TagViewSet,
    FavoriteViewSet,

)

v1_router = DefaultRouter()
v1_router.register('recipes', RecipeViewSet, basename='recipe')
v1_router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredient'
)
v1_router.register('tags', TagViewSet, basename='tag')
v1_router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorite'
)

urlpatterns = [
    path('', include(v1_router.urls)),
]
