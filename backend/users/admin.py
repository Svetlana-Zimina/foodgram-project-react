from django.contrib import admin

from .models import User, Subscription


class UserAdmin(admin.ModelAdmin):
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
    list_display = (
        'user',
        'following',
    )

    class Meta:
        ordering = ('user', )


admin.site.register(User, UserAdmin)  
admin.site.register(Subscription, SubscriptionAdmin)
