from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.constraints import (
    CheckConstraint,
    UniqueConstraint
)
from django.db.models import F, Q


class User(AbstractUser):
    """Кастомная модель User."""

    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Логин пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия пользователя'
    )
        
    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.username


class Subscription(models.Model):
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

