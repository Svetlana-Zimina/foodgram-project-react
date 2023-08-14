import re

from rest_framework import serializers
from users.models import User


def validate_restricted_username(value):
    if value.lower() == "me":
        raise serializers.ValidationError('there is no "me" allowed!')
    return value


def validate_bad_username(value):
    if not re.match(r"^[\w.@+-]+$", value):
        raise serializers.ValidationError(
            "this signs are not allowed",
        )
    return value


def validate_email(value):
    new_email = value.lower()
    if User.objects.filter(email=new_email).exists():
        raise serializers.ValidationError('you cannot reuse the same email')
    return value
