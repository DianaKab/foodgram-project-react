from django.contrib import admin
from .models import *


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author',)
    list_filter = ('author', 'name', 'tags',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
admin.site.register(IngredientRecipe)
admin.site.register(TagRecipe)
