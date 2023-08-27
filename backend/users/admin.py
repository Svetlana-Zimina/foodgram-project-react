from django.contrib import admin

from .models import Subscription, User


class UserAdmin(admin.ModelAdmin):
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


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
