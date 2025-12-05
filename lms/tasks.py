from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from lms.models import Course, Subscription


@shared_task
def send_course_update_email(course_id):
    """Отправляет письма подписчикам при обновлении курса."""
    course = Course.objects.get(id=course_id)

    subscribers = Subscription.objects.filter(course=course)
    recipients = list(subscribers.values_list('user__email', flat=False))

    if not recipients:
        return "Нет подписчиков с email"

    subject = f"Обновление курса: {course.name}"
    message = (
        f"Материалы курса '{course.name}' были обновлены. "
        f"Проверьте новые уроки на платформе!"
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=False,
    )

    return f"Отправлено писем: {len(recipients)}"
