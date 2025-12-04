from rest_framework.serializers import ValidationError


def validate_video_url(value):
    """Валидация ссылок: принимаются только от youtube"""
    if not value.startswith("https://www.youtube.com"):
        raise ValidationError("Использованы сторонние ссылки")
    return value
