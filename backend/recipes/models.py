import shortuuid
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from recipes.recipes_const import (
    CHAR_FIELD_MAX_LENGTH, MAX_COOKING_TIME,
    MAX_AMOUNT, MAX_SHORT_LINK_LENGTH,
    MIN_AMOUNT, MIN_COOKING_TIME,
    SHORT_LINK_LENGTH)
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=CHAR_FIELD_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=CHAR_FIELD_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name'),


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Тег',
        unique=True,
        max_length=CHAR_FIELD_MAX_LENGTH,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Рецепт',
        max_length=CHAR_FIELD_MAX_LENGTH,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/'
    )
    text = models.TextField(
        verbose_name='Описание',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        auto_now_add=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления блюда',
        validators=[
            MinValueValidator(MIN_COOKING_TIME,
                              message='Не менее одной минуты!'),
            MaxValueValidator(MAX_COOKING_TIME,
                              message='Это очень долго!'),
        ],
    )
    short_link = models.CharField(
        verbose_name='Короткая ссылка',
        max_length=MAX_SHORT_LINK_LENGTH,
        blank=True,
        null=True,
        unique=True,
    )

    def get_or_create_short_link(self):
        if not self.short_link:
            self.short_link = shortuuid.uuid()[:SHORT_LINK_LENGTH]
            self.save(update_fields=['short_link'])
        return self.short_link

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(MIN_AMOUNT, message='Не менее 1!'),
            MaxValueValidator(MAX_AMOUNT, message='Не более 32000!'),
        ],
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        ordering = ('id',)


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite_recipe'
            ),
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='in_shopping_cart',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_shopping_cart_recipe'
            ),
        )
