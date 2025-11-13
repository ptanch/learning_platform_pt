from django.db import models


class Course(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="Название курса",
        help_text="Укажите название курса",
    )
    preview = models.ImageField(
        upload_to="lms/preview",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите фото курса",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание курса",
        help_text="Укажите описание курса",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        verbose_name="Курс",
        help_text="Выберите курс",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Название урока",
        help_text="Укажите название урока",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание урока",
        help_text="Укажите описание урока",
    )
    photo = models.ImageField(
        upload_to="lms/photo",
        blank=True,
        null=True,
        verbose_name="Фото",
        help_text="Загрузите фото урока",
    )
    video_link = models.URLField(blank=True, null=True, verbose_name="Видео урока")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
