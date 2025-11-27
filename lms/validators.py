from rest_framework.serializers import ValidationError


def validate_video_url(value):
    if not value.startswith("https://www.youtube.com"):
        raise ValidationError("Использованы сторонние ссылки")
    return value
