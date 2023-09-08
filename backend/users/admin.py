from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class CustomUserAdmin(UserAdmin):
    """Настройки модели Пользователя
    lля отображения в панели администратора"""

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name'
    )
    list_filter = ('email', 'username')

    class Meta:
        ordering = ('username', )


class SubscriptionAdmin(admin.ModelAdmin):
    """Настройки модели Подписки
    lля отображения в панели администратора"""

    list_display = (
        'user',
        'following',
    )

    class Meta:
        ordering = ('user', )


admin.site.register(User, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
