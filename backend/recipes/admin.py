from django.contrib import admin

from .models import (
    Recipe,
    Ingredient,
    Tag,
    Favorite,
    ShoppingCart
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author'
    ) 
    list_filter = ('name', 'author', 'tags')

    def count_favorite(self, instance):
        return instance.lover.count()

    count_favorite.short_description = 'Добавили в избранное'

    
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    ) 
    list_filter = ('name', )

    class Meta:
        ordering = ('name', )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug'
    ) 


class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
    list_filter = ('user', )

    class Meta:
        ordering = ('user', )


class ShoppingCartAdmin(admin.ModelAdmin):
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
    