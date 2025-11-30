from requests import session
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
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class UserUpdateApiView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileApiView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDeleteApiView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class PaymentsListApiView(ListAPIView):
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializer

    filter_backends = [OrderingFilter]
    ordering_fields = ["payment_date"]

    def get_queryset(self):
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
    queryset = Payments.objects.all()
    serializer_class = PaymentsSerializer

    def perform_create(self, serializer):
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
