from django.core.exceptions import ValidationError


def validate_username_me(value):
    if value.lower() == "me":
        raise ValidationError('Имя пользователя не должно быть "me"!')
    return value
