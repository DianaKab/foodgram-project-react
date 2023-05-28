from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator


from .models import Subscribe, User


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'user', 'following',)
        model = Subscribe

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=['user', 'following'],
                message='Ты уже подписан!'
            )
        ]

    def validate_following(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError("Нельзя подписаться на себя!")
        return value


class UsersCreateSerializer(UserCreateSerializer):
    """Сериализатор для обработки запросов на создание пользователя.
    Валидирует создание пользователя с юзернеймом 'me'."""
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password')

        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        if value == "me":
            raise ValidationError(
                'Невозможно создать пользователя с таким именем!'
            )
        return value

    def validate_email(self, value):
        return value.lower()


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
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
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


class FollowSerializer(CustomUserSerializer):
    """Сериализатор для добавления/удаления подписки, просмотра подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        from app.serializers import RecipeSerializer

        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipe_limit')
        queryset = obj.recipe.all()
        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]
        return RecipeSerializer(queryset, context=context, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipe.count()

    class Meta:
        model = Subscribe
        fields = ('user', 'following', 'recipes', 'recipes_count')
