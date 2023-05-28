import base64

from app.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                        ShoppingCart, Tag)
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator
from users.serializers import CustomUserSerializer


def add_ingredient(ingredients, obj):
    for ingredient in ingredients:
        current_ingredient = get_object_or_404(
            Ingredient, pk=ingredient["id"]
        )
        ingredient_recipe, status = IngredientRecipe.objects.get_or_create(
            ingredient=current_ingredient,
            amount=ingredient["amount"]
        )
        obj.ingredients.add(ingredient_recipe.id)
    return obj


class TagSerializer(serializers.ModelSerializer):
    """Получение тегов."""

    class Meta:
        fields = ('id', 'name', 'color', 'slug')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit', )
        model = Ingredient


class Base64ImageField(serializers.ImageField):
    """Преобразование картинки из Base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class FavoriteSerializer(serializers.ModelSerializer):
    """Добавление/удаление избранных авторов."""

    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        queryset=Recipe.objects.all()
    )
    name = serializers.StringRelatedField(
        source='recipe.name'
    )
    image = serializers.FileField(
        source='recipe.image',
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
    )

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
            )
        model = Favorite

        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Добавление/удаление/получение списка покупок."""

    id = serializers.PrimaryKeyRelatedField(
        source='recipe',
        queryset=Recipe.objects.all()
    )
    name = serializers.StringRelatedField(
        source='recipe.name'
    )
    image = serializers.FileField(
        source='recipe.image',
    )
    cooking_time = serializers.IntegerField(
        source='recipe.cooking_time',
    )

    class Meta:
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        model = ShoppingCart

        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe')
            )
        ]


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """Получение ингредиентов в списке рецептов."""

    name = serializers.StringRelatedField(
        source='ingredient.name'
    )
    measurement_unit = serializers.StringRelatedField(
        source='ingredient.measurement_unit'
    )
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
            )
        model = IngredientRecipe


class IngredientCreateInRecipeSerializer(serializers.ModelSerializer):
    """Добавление ингредиентов в рецепт."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        fields = (
            'id',
            'amount'
            )
        model = IngredientRecipe


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id',
                  'image',
                  'name',
                  'cooking_time',
                  )
        model = Recipe


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/изменение рецепта."""

    ingredients = IngredientCreateInRecipeSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = ('id',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'tags',
                  'image',
                  'name',
                  'text',
                  'cooking_time',
                  )
        model = Recipe

    def validate_ingredients(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Добавьте хотя бы один ингредиент.")
        return value

    def validate_tags(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Добавьте хотя бы один тег.")
        return value

    def create(self, validated_data):
        validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        ingredients = self.initial_data.pop('ingredients')
        tags = self.initial_data.pop('tags')
        recipe.tags.set(tags)
        return add_ingredient(ingredients, recipe)

    def update(self, instance, validated_data):
        instance.tags.clear()
        instance.ingredients.clear()
        validated_data.pop('ingredients')
        ingredients = self.initial_data.pop('ingredients')
        tags = self.initial_data.pop('tags')
        instance.tags.set(tags)
        add_ingredient(ingredients, instance)
        super().update(instance, validated_data)
        instance.save()
        return instance

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user, recipe=obj
        ).exists()

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return GetRecipeSerializer(instance, context=context).data


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения полной информации о рецепте."""
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(read_only=True, many=True,
                                             source='recipe_ingredient')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return object.carts.filter(user=user).exists()
