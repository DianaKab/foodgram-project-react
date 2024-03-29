import io

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .mixins import ListRetrieveViewSet
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)
from .permissions import *
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer,
                          ShoppingCartSerializer, TagSerializer)
from .paginations import LimitPagination


def add_to(model, user, pk, serializer_class):
    """Создание экземпляра"""
    recipe = get_object_or_404(Recipe, pk=pk)
    instance = model.objects.create(user=user, recipe=recipe)
    serializer = serializer_class(instance)
    return Response(data=serializer.data, status=status.HTTP_201_CREATED)


def delete_from(model, user, pk):
    """Удаление экземпляра"""

    if model.objects.filter(user=user, recipe__id=pk).exists():
        model.objects.filter(
            user=user, recipe__id=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ListRetrieveViewSet):
    """Класс вьюсета тегов"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    """Класс вьюсета ингредиетов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс вьюсета рецептов"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateUpdateSerializer
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
        serializer_class=FavoriteSerializer
    )
    def favorite(self, request, pk):
        """Создание/удаление избранных рецептов пользователя"""

        if request.method == 'POST':
            serializer_class = FavoriteSerializer
            return add_to(Favorite, request.user, pk, serializer_class)
        return delete_from(Favorite, request.user, pk)

    @action(
        detail=False,
        permission_classes=(IsAuthor,),
        pagination_class=None,
    )
    def download_shopping_cart(self, request) :
        """Скачивания списка покупок пользователя"""
        ingredients = list(IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(Sum('amount')))
        file_data = []

        for ingredient in ingredients :
            file_data.append(f'{ingredient[0]} ({ingredient[1]}) - {ingredient[2]}\n')
        response = HttpResponse(file_data, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_car.txt"'

        return response

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthor,),
        serializer_class=ShoppingCartSerializer
    )
    def shopping_cart(self, request, pk) :
        """Создание/удаление списка покупок пользователя"""

        if request.method == 'POST':
            serializer_class = ShoppingCartSerializer
            return add_to(ShoppingCart, request.user, pk, serializer_class)
        return delete_from(ShoppingCart, request.user, pk)
