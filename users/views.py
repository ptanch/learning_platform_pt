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
