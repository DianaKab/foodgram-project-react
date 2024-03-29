from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views
from users.views import CustomUserViewSet

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'users', CustomUserViewSet, basename='user')


urlpatterns = [
    path(r'', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
