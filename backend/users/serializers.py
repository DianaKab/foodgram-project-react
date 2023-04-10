from rest_framework import serializers
from djoser.serializers import UserSerializer
from .models import User, Subscribe


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'user', 'following',)
        model = Subscribe


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['username'],
            last_name=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            user=request.user, following=obj
        ).exists()
