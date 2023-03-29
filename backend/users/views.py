from rest_framework import viewsets
from djoser.views import UserViewSet
from rest_framework.decorators import action
from .models import User
from .serializers import CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        pass

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, pk=None):
        followings = Subscribe.objects.get(pk=pk)
        return Response({'followings': followings.name})

