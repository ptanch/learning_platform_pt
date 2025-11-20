from django.urls import path
from users import views
from users.apps import UsersConfig
from users.views import PaymentsListApiView, UserCreateApiView
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
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
