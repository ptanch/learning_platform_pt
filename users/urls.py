from django.urls import path
from rest_framework.permissions import AllowAny

from users import views
from users.apps import UsersConfig
from users.views import PaymentsListApiView, UserCreateApiView, UserDeleteApiView, PaymentsCreateApiView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("create/", views.UserCreateApiView.as_view(), name="create"),
    path("profile/", views.UserProfileApiView.as_view(), name="profile"),
    path("payments/", PaymentsListApiView.as_view(), name="payments_list"),
    path("register/", UserCreateApiView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(permission_classes=(AllowAny,)), name="token_refresh"),
    path("user/<int:pk>/delete/", UserDeleteApiView.as_view(), name="user_delete"),
    path("payments/create/", PaymentsCreateApiView.as_view(), name="create_payments"),
]
