from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SerializerMethodField

from .models import User
from recipes.models import Recipe


class CustomUserSerializer(UserSerializer):
    avatar = Base64ImageField()
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'avatar',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def validate(self, attrs):
        request = self.context.get('request')
        if request and 'avatar' not in attrs or attrs.get('avatar') is None:
            raise serializers.ValidationError("Отсутствует поле 'avatar'")
        return super().validate(attrs)

    def update(self, instance, validated_data):
        avatar = validated_data.get('avatar', None)
        if avatar:
            if instance.avatar:
                instance.avatar.delete()
            instance.avatar = avatar
        return super().update(instance, validated_data)

    def get_is_subscribed(self, obj):
        user = self.context.get('request')
        print('........get_is_subscribed...........')
        return user.user.subscribes.filter(author=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class SubscriptionSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'avatar',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if user.subscribes.filter(author=author).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if user == author:
            raise ValidationError(
                detail='Невозможно подписаться на самого себя!',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data

    def get_recipes(self, obj):
        from recipes.serializers import RecipeSimpleListSerializer
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeSimpleListSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()