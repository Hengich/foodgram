from django.db.models import F
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from recipes.recipes_const import (MIN_COOKING_TIME,
                                   MIN_AMOUNT,
                                   MAX_COOKING_TIME,
                                   MAX_AMOUNT)
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientsCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=MIN_AMOUNT,
                                      max_value=MAX_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSimpleListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    image = serializers.ReadOnlyField(source='image.url')
    tags = TagSerializer(many=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME,
                                            max_value=MAX_COOKING_TIME)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()

    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe_ingredients__amount')
        )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'tags',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'cooking_time',
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsCreateSerializer(
        many=True,
    )
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME,
                                            max_value=MAX_COOKING_TIME)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = self.context['request'].data.get('tags', [])
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        self.add_ingredients(ingredients, recipe)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = self.context['request'].data.get('ingredients', [])
        tags = self.context['request'].data.get('tags', [])

        image = validated_data.pop('image', None)
        if image:
            instance.image = image

        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.recipeingredients.all().delete()
        self.add_ingredients(ingredients, instance)
        return instance

    def add_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient_id=ingredient['id'],
                    amount=ingredient['amount'],
                )
                for ingredient in ingredients
            ]
        )

    def validate(self, data):
        if self.instance is None and not data.get('image'):
            raise ValidationError('Необходимо изображение рецепта.')

        request = self.context['request']
        tags = request.data.get('tags', [])
        ingredients = request.data.get('ingredients', [])

        if not tags:
            raise ValidationError('Необходимо выбрать хотя бы один тэг.')

        if not ingredients:
            raise ValidationError('Необходимо добавить хотя '
                                  'бы один ингредиент.')

        checked_tags = set()
        for tag in tags:
            if tag in checked_tags:
                raise ValidationError('Нельзя использовать повторяющиеся '
                                      'тэги .')
            if not Tag.objects.filter(id=tag).exists():
                raise ValidationError(f'Указан несуществующий тэг - {tag}.')
            checked_tags.add(tag)

        checked_ingredients = set()
        for ingredient in ingredients:
            if ingredient['id'] in checked_ingredients:
                raise ValidationError('Нельзя использовать два '
                                      'одинаковых ингредиента.')
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise ValidationError(f'Указан несуществующий ингредиент '
                                      f'- {ingredient}.')
            checked_ingredients.add(ingredient['id'])
        return data

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance, context={"request": self.context.get("request")}
        ).data

    class Meta:
        model = Recipe
        exclude = ('pub_date',)
