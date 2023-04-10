from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views

from .views import TagViewSet, IngredientViewSet, RecipeViewSet
from users.views import CustomUserViewSet, SubscribeViewSet

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'users', SubscribeViewSet, basename='subscribe')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/token/login/', views.obtain_auth_token),
]
