from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from django.db import IntegrityError
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from .models import (
    User,
    Subscription
)

from .validators import (
    validate_bad_username,
    validate_email,
    validate_restricted_username,
)


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            validate_bad_username,
            validate_restricted_username,
            validate_email,
        ],
    )
    email = serializers.EmailField(max_length=254)

    def create(self, validated_data):
        try:
            user = User.objects.get_or_create(**validated_data)[0]
        except IntegrityError:
            raise serializers.ValidationError(
                'Имя пользователя или email уже существуют.'
            )
        return user

    class Meta:
        model = User
        fields = ('email', 'username')


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        model = User
        read_only_fields = ("role",)


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Subscription."""

    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username'
    )

    class Meta:
        fields = ('user', 'following')
        model = Subscription
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'following'),
                message='На этого автора вы уже подписаны!'
            ),
        ]

    def validate_subscription(self, value):
        """Проверка, что пользователь не подписывается на себя."""

        if value == self.context['request'].user:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return value
