from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from users.models import User


@shared_task
def deactivate_inactive_users():
    """
    Блокирует пользователей, которые не заходили более месяца.
    """
    month_ago = timezone.now() - relativedelta(months=1)
    inactive_users = User.objects.filter(last_login__lt=month_ago, is_active=True)

    count = inactive_users.update(is_active=False)
    return f"Заблокировано пользователей: {count}"
