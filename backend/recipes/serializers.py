from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from recipes.recipes_const import (MIN_AMOUNT, MAX_AMOUNT,
                                   MIN_COOKING_TIME, MAX_COOKING_TIME)
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
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientsCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(min_value=MIN_AMOUNT,
                                      max_value=MAX_AMOUNT)

    class Meta:
        model = Ingredient
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
    ingredients = RecipeIngredientsSerializer(
        many=True, required=True, source='recipe_ingredients'
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
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsCreateSerializer(many=True)
    cooking_time = serializers.IntegerField(min_value=MIN_COOKING_TIME,
                                            max_value=MAX_COOKING_TIME)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        self.add_ingredients(recipe, ingredients_data)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients', [])
        tags = validated_data.pop('tags', [])
        image = validated_data.pop('image', None)

        if image:
            instance.image = image
        instance = super().update(instance, validated_data)

        instance.tags.set(tags)
        instance.recipe_ingredients.clear()
        self.add_ingredients(instance, ingredients_data)
        return instance

    def add_ingredients(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient_data['id'],
                amount=ingredient_data['amount'],
            )

    def validate(self, data):
        request = self.context['request']
        tags = request.data.get('tags', [])
        ingredients = request.data.get('ingredients', [])

        if not tags:
            raise ValidationError('Необходимо выбрать хотя бы один тэг.')
        if not ingredients:
            raise ValidationError('Необходимо добавить хотя бы один ингредиент.')

        # Validate for unique tags and existing tags
        if len(tags) != len(set(tags)):
            raise ValidationError('Нельзя использовать повторяющиеся тэги.')
        for tag_id in tags:
            if not Tag.objects.filter(id=tag_id).exists():
                raise ValidationError(f'Указан несуществующий тэг - {tag_id}.')

        # Validate for unique ingredients and existing ingredients
        unique_ingredients = set()
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            if ingredient_id in unique_ingredients:
                raise ValidationError('Нельзя использовать два одинаковых ингредиента.')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise ValidationError(f'Указан несуществующий ингредиент - {ingredient_id}.')
            unique_ingredients.add(ingredient_id)

        return data

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

