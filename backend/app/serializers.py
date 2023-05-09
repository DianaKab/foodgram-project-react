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


class RecipeListSerializer(serializers.ModelSerializer):
    """Получение списка рецептов/рецепта."""

    author = CustomUserSerializer(read_only=True)
    tags = serializers.SerializerMethodField()
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = serializers.SerializerMethodField()

    def get_ingredients(self, obj):
        """Возвращает отдельный сериализатор."""
        return IngredientRecipeSerializer(
            IngredientRecipe.objects.filter(recipe__id=obj.id).all(), many=True
        ).data

    def get_tags(self, obj):
        """Возвращает отдельный сериализатор."""
        return TagSerializer(
            Tag.objects.filter(recipe__id=obj.id).all(), many=True
        ).data

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


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Создание/изменение рецепта."""

    ingredients = IngredientCreateInRecipeSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    # tags = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
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

    def get_tags(self, obj) :
        """Возвращает отдельный сериализатор."""
        return TagSerializer(
            Tag.objects.filter(recipe__id=obj.id).all(), many=True
        ).data

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

    def to_representation(self, obj):
        """Возвращаем прдеставление в таком же виде, как и GET-запрос."""
        self.fields.pop('ingredients')
        representation = super().to_representation(obj)
        representation['ingredients'] = IngredientRecipeSerializer(
            IngredientRecipe.objects.filter(recipe__id=obj.id).all(), many=True
        ).data
        return representation


class RecipeInSubscribtionSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        fields = ('id',
                  'image',
                  'name',
                  'cooking_time',
                  )
        model = Recipe
