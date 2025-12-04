from rest_framework.filters import OrderingFilter
from rest_framework.generics import (
    CreateAPIView,
    UpdateAPIView,
    RetrieveUpdateAPIView,
    ListAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.models import User, Payments
from users.serializers import UserSerializer, PaymentsSerializer
from users.services import create_stripe_price, create_stripe_session, create_stripe_product


class UserCreateApiView(CreateAPIView):
    """
    API view для создания пользователя.
    Позволяет регистрировать новых пользователей без аутентификации.
    При создании автоматически активирует аккаунт (is_active=True) и корректно хеширует пароль
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        """Создаёт пользователя, активирует его и устанавливает хешированный пароль"""
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserUpdateApiView(UpdateAPIView):
    """
    API view для обновления данных пользователя.
    Требует аутентификации (наследуется от базового класса).
    Позволяет изменять любые поля пользователя через UserSerializer
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileApiView(RetrieveUpdateAPIView):
    """
    API view для получения и обновления профиля текущего пользователя.
    Доступ разрешён только аутентифицированным пользователям.
    Всегда работает с объектом запроса пользователя (request.user)
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Возвращает объект текущего пользователя из запроса"""
        return self.request.user


class UserDeleteApiView(DestroyAPIView):
    """
    API view для удаления пользователя.
    Доступ разрешён только аутентифицированным пользователям.
    Удаляет указанный объект пользователя из базы данных
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class PaymentsListApiView(ListAPIView):
    """API view для получения списка платежей с фильтрацией и сортировкой"""
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializer

    filter_backends = [OrderingFilter]
    ordering_fields = ["payment_date"]

    def get_queryset(self):
        """Формирует отфильтрованный набор платежей на основе параметров запроса"""
        queryset = super().get_queryset()

        # Фильтрация по курсу
        paid_course = self.request.query_params.get("paid_course")
        if paid_course:
            queryset = queryset.filter(paid_course_id=paid_course)

        # Фильтрация по уроку
        paid_lesson = self.request.query_params.get("paid_lesson")
        if paid_lesson:
            queryset = queryset.filter(paid_lesson_id=paid_lesson)

        # Фильтрация по способу оплаты
        payment_method = self.request.query_params.get("payment_method")
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        return queryset


class PaymentsCreateApiView(CreateAPIView):
    """API view для создания платежа и интеграции со Stripe"""
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializer

    def perform_create(self, serializer):
        """Создаёт платёж и настраивает интеграцию со Stripe"""
        payment = serializer.save(user=self.request.user)

        course = payment.paid_course
        amount = payment.amount

        product_id = create_stripe_product(course)

        price_id = create_stripe_price(course, amount)

        session_id, session_url = create_stripe_session(price_id)

        payment.stripe_session_id = session_id
        payment.payment_url = session_url
        payment.payment_method = "stripe"
        payment.save()
