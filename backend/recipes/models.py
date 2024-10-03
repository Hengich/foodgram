from cryptography.hazmat.backends.openssl import backend
from django.db import models

from users.models import User

from recipes.recipes_const import CHAR_FIELD_MAX_LENGTH


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
        ordering = ('name',),


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
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


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
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
