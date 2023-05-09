import io

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination, LimitPagination
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from users.models import User

from .mixins import ListRetrieveViewSet
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)
from .permissions import *
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeListSerializer,
                          ShoppingCartSerializer, TagSerializer)


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
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    """Класс вьюсета ингредиетов"""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс вьюсета рецептов"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeCreateUpdateSerializer
    pagination_class = LimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags', )
    permission_classes = (IsAuthorOrReadOnly,)

    def get_permissions(self):
        if self.action == 'retrieve':
            return (ReadOnly(),)
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer

        return RecipeListSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite',
        filter_backends=(DjangoFilterBackend,),
        filterset_fields=('tags',),
        permission_classes=(IsAuthor,),
        serializer_class=RecipeListSerializer
    )
    def get_favorite(self, request, pk):
        """Создание/удаление избранных рецептов пользователя"""

        if request.method == 'POST':
            serializer_class = FavoriteSerializer
            return add_to(Favorite, request.user, pk, serializer_class)
        return delete_from(Favorite, request.user, pk)

    @action(
        detail=False,
        permission_classes=(IsAuthor,)
    )
    def download_shopping_cart(self, request):
        """Скачивания списка покупок пользователя"""

        ingredients = list(IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(Sum('amount')))
        file_data = []
        for ingredient in ingredients:
            file_data.append(f'{ingredient[0]} ({ingredient[1]}) - {ingredient[2]}\n')
        response = HttpResponse(file_data, content_type='application/text charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="shopping_car.txt"'
        return response

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=(IsAuthor,)
    )
    def get_shopping_cart(self, request, pk):
        """Создание/удаление списка покупок пользователя"""

        if request.method == 'POST':
            serializer_class = ShoppingCartSerializer
            return add_to(ShoppingCart, request.user, pk, serializer_class)
        return delete_from(ShoppingCart, request.user, pk)
