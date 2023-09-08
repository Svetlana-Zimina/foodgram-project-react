from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.constraints import CheckConstraint, UniqueConstraint

from foodgram_backend import constants
from .validators import validate_username_me


class User(AbstractUser):
    """Кастомная модель Пользователя."""

    email = models.EmailField(
        max_length=constants.MAX_LENGTH_3,
        unique=True,
        verbose_name='Адрес электронной почты'
    )
    username = models.CharField(
        max_length=constants.MAX_LENGTH_4,
        unique=True,
        verbose_name='Имя пользователя',
        validators=[
            UnicodeUsernameValidator(),
            validate_username_me
        ],
    )
    first_name = models.CharField(
        max_length=constants.MAX_LENGTH_4,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=constants.MAX_LENGTH_4,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=constants.MAX_LENGTH_4,
        verbose_name='Пароль'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель Подписка."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь на которого подписались'
    )

    class Meta:
        ordering = ('user',)
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            CheckConstraint(
                check=~Q(user=F('following')),
                name='could_not_subscribe_itself'
            ),
            UniqueConstraint(
                fields=['user', 'following'],
                name='unique_subscription'
            ),
        ]
