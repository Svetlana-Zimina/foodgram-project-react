from django.urls import include, path
from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from rest_framework.routers import DefaultRouter

v1_router = DefaultRouter()
v1_router.register('recipes', RecipeViewSet, basename='recipe')
v1_router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredient'
)
v1_router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(v1_router.urls)),
]
