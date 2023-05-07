from app.permissions import *
from app.serializers import RecipeInSubscribtionSerializer
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Subscribe, User
from .serializers import CustomUserSerializer, SubscribeSerializer


class CustomUserViewSet(UserViewSet):
    """Класс вьюсета пользователя"""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination

    @action(
        methods=['get'],
        detail=False,
        serializer_class=SubscribeSerializer,
        permission_classes=(IsAuthor,),
        pagination_class=PageNumberPagination
    )
    def subscriptions(self, request) :
        """Класс вьюсета подписок пользователя"""

        subscribes = Subscribe.objects.filter(user=request.user)
        page = self.paginate_queryset(subscribes)
        serializer = SubscribeSerializer(
            page, many=True,
            context={'request' : request})
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True
    )
    def subscribe(self, request, pk) :
        """Класс вьюсета подписки/отписки пользователя"""

        serializer_class = SubscribeSerializer
        if request.method == 'POST' :
            following = get_object_or_404(User, pk=pk)
            instance = Subscribe.objects.create(user=request.user, following=following)
            serializer = serializer_class(instance)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else :
            if Subscribe.objects.filter(user=request.user, following__id=pk).exists() :
                Subscribe.objects.filter(
                    user=request.user, following__id=pk
                ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_400_BAD_REQUEST)
