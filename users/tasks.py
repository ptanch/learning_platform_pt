from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from users.models import User


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца.
    """
    now = timezone.now()
    inactive_period = now - timedelta(days=30)  # 30 дней
    inactive_users = User.objects.filter(last_login__lt=inactive_period, is_active=True)

    count = inactive_users.update(is_active=False)
    return f"Заблокировано пользователей: {count}"
