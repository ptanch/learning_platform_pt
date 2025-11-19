from django.utils import timezone

from django.core.management import BaseCommand

from users.models import Payments, User
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = 'Create sample payment records'

    def handle(self, *args, **kwargs):
        Payments.objects.all().delete()

        users = list(User.objects.all())
        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR("В базе нет пользователей! Загрузите фикстуру users.json"))
            return

        if not courses:
            self.stdout.write(self.style.ERROR("Нет курсов! Создайте через Postman."))
            return

        if not lessons:
            self.stdout.write(self.style.ERROR("Нет уроков! Создайте через Postman."))
            return

        Payments.objects.create(
            user=users[0],
            payment_date=timezone.now(),
            paid_course=courses[0],
            paid_lesson=None,
            amount="1500.00",
            payment_method="cash",
        )

        # Платеж за урок
        Payments.objects.create(
            user=users[1] if len(users) > 1 else users[0],
            payment_date=timezone.now(),
            paid_course=None,
            paid_lesson=lessons[0],
            amount="500.00",
            payment_method="transfer",
        )

        # Платеж за другой курс
        Payments.objects.create(
            user=users[0],
            payment_date=timezone.now(),
            paid_course=courses[1],
            paid_lesson=None,
            amount="2000.00",
            payment_method="transfer",
        )

        # Платеж за другой урок
        Payments.objects.create(
            user=users[1] if len(users) > 1 else users[0],
            payment_date=timezone.now(),
            paid_course=None,
            paid_lesson=lessons[3],
            amount="700.00",
            payment_method="cash",
        )

        self.stdout.write(self.style.SUCCESS("Платежи успешно созданы."))
