from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from .mixins import ListRetrieveViewSet
from .serializers import \
    TagSerializer, \
    IngredientSerializer, \
    RecipeSerializer, \
    FavoriteSerializer, \
    ShoppingCartSerializer


def add_to(model, user, pk, serializer_class):
    recipe = get_object_or_404(Recipe, pk=pk)
    instance = model.objects.create(user=user, recipe=recipe)
    serializer = serializer_class(instance)
    # serializer.is_valid(raise_exception=True)
    return Response(data=serializer.data, status=status.HTTP_201_CREATED)


def delete_from(model, user, pk):
    if model.objects.filter(user=user, recipe__id=pk).exists():
        model.objects.filter(
            user=user, recipe__id=pk
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite'
    )
    def get_favorite(self, request, pk):
        if request.method == 'POST':
            serializer_class = FavoriteSerializer
            return add_to(Favorite, request.user, pk, serializer_class)
        return delete_from(Favorite, request.user, pk)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        pass

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart'
    )
    def get_shopping_cart(self, request, pk):
        if request.method == 'POST':
            serializer_class = ShoppingCartSerializer
            return add_to(ShoppingCart, request.user, pk, serializer_class)
        return delete_from(ShoppingCart, request.user, pk)

