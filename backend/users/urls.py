from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import (
    UserViewSet,
    SubscriptionViewSet
)

urlpatterns = [
    path('', include('djoser.urls')),  # Работа с пользователями
    path('auth/', include('djoser.urls.authtoken')),  # Работа с токенами
]
