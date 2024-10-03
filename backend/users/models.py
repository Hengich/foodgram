from django.db import models
from django.contrib.auth.models import AbstractUser

from .users_const import EMAIL_MAX_LENGTH, NAME_MAX_LENGTH


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='Почта',
        unique=True,
        max_length=EMAIL_MAX_LENGTH,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=NAME_MAX_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=NAME_MAX_LENGTH,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='author',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = [
            models.UniqueConstraint(
                name='unique_subscription',
                fields=('author', 'user'),
            )
        ]
