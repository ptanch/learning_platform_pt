from datetime import timedelta

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    get_object_or_404,
)

from lms.models import Course, Lesson, Subscription
from lms.paginations import CustomPagination
from lms.serializers import CourseSerializer, LessonSerializer, CourseDetailSerializer
from lms.tasks import send_course_update_email
from users.permissions import IsModer, IsOwner


class CourseViewSet(ModelViewSet):
    """ViewSet для управления курсами"""
    queryset = Course.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        """Определяет сериализатор в зависимости от действия"""
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        """Сохраняет объект курса и назначает текущего пользователя владельцем"""
        course = serializer.save()
        course.owner = self.request.user
        course.save()

    def perform_update(self, serializer):
        """
        Обновляет курс и отправляет email‑уведомление при необходимости
        (если прошло ≥ 4 часов с последнего уведомления)
        """
        updated_course = serializer.save()

        now = timezone.now()
        last_sent = updated_course.last_notification_sent

        # Если не было уведомления или прошло больше 4 часов
        if not last_sent or (now - last_sent) >= timedelta(hours=4):
            send_course_update_email.delay(updated_course.id)
            updated_course.last_notification_sent = now
            updated_course.save(update_fields=["last_notification_sent"])

        return updated_course

    def get_permissions(self):
        """Настраивает классы разрешений в зависимости от действия"""
        if self.action == "create":
            self.permission_classes = (~IsModer,)
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = (IsModer | IsOwner,)
        elif self.action == "destroy":
            self.permission_classes = (IsOwner | ~IsModer,)
        return super().get_permissions()


class LessonCreateApiView(CreateAPIView):
    """
    API view для создания урока.
    Требует аутентификации и запрещает создание уроков модераторам.
    При создании назначает текущего пользователя владельцем урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (~IsModer, IsAuthenticated)

    def perform_create(self, serializer):
        """Сохраняет объект урока и назначает текущего пользователя владельцем"""
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()


class LessonListApiView(ListAPIView):
    """
    API view для получения списка уроков.
    Возвращает уроки, упорядоченные по ID, с пагинацией
    """
    queryset = Lesson.objects.all().order_by("id")
    serializer_class = LessonSerializer
    pagination_class = CustomPagination


class LessonRetrieveApiView(RetrieveAPIView):
    """
    API view для получения детальной информации об уроке.
    Требует аутентификации; доступ разрешён модераторам или владельцу урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsModer | IsOwner)


class LessonUpdateApiView(UpdateAPIView):
    """
    API view для обновления урока.
    Требует аутентификации; доступ разрешён модераторам или владельцу урока
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsModer | IsOwner)


class LessonDestroyApiView(DestroyAPIView):
    """
    API‑вью для удаления урока.
    Требует аутентификации; доступ разрешён владельцу ИЛИ не‑модератору
    """
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsOwner | ~IsModer)


class SubscriptionApiView(APIView):
    """
    Управление подпиской пользователя на курс.
    Позволяет подписываться на курс или отписываться от него.
    Требует аутентификации
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Обрабатывает POST‑запрос на управление подпиской"""
        user = request.user
        course_id = request.data.get("course")

        if not course_id:
            return Response({"error": "Не передан course_id"}, status=400)

        course_item = get_object_or_404(Course, id=course_id)

        subs_item = Subscription.objects.filter(user=user, course=course_item)

        if subs_item.exists():
            subs_item.delete()
            message = "Подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "Подписка добавлена"

        return Response({"message": message})
