import base64
from django.core.files.base import ContentFile
from app.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart, IngredientRecipe, TagRecipe
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework.relations import SlugRelatedField
from users.serializers import CustomUserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'recipes')
        model = Tag


class TagRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'tag', 'recipe', 'recipes')
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit', )
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


class IngredientRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = (
            'id',
            'amount'
            )
        model = IngredientRecipe


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = IngredientRecipeSerializer(many=True, source='ingredients_recipes')

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

    def create(self, validated_data):
        validated_data.pop('ingredients_recipes')
        recipe = Recipe.objects.create(**validated_data)
        ingredients = self.initial_data.pop('ingredients')
        tags = self.initial_data.pop('tags')
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient_id=ingredient["id"],
                amount=ingredient["amount"],
                recipe=recipe
            )
        for tag in tags:
            TagRecipe.objects.create(
                tag_id=tag,
                recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        validated_data.pop('ingredients_recipes')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        ingredients = self.initial_data.pop('ingredients')
        tags = self.initial_data.pop('tags')
        instance.tags.set(tags)
        lst = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient, pk=ingredient["id"]
            )
            IngredientRecipe.objects.create(
                recipe=instance,
                ingredient=current_ingredient,
                amount=ingredient["amount"],
            )
            lst.append(current_ingredient)
        instance.ingredients.set(lst)
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
