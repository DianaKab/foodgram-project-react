import base64

from django.core.files.base import ContentFile
from app.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart, IngredientRecipe, TagRecipe
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name',)
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit',)
        model = Ingredient


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'recipe',
            'user',
            )
        model = Favorite


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'recipe',
            'user',
            )
        model = ShoppingCart


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)
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
                  'cooking_time')
        model = Recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient)
            # И связываем каждое достижение с этим котиком
            IngredientRecipe.objects.create(
                ingredient=current_ingredient, recipe=recipe)
        for tag in tags :
            current_tag, status = Tag.objects.get_or_create(
                **tag)
            # И связываем каждое достижение с этим котиком
            TagRecipe.objects.create(
                tag=current_tag, recipe=recipe)
        return recipe

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
            user=request.user, shop_recipe=obj
        ).exists()
