from django.urls import path
from users import views
from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path('create/', views.UserCreateApiView.as_view(), name='create'),
    path('profile/', views.UserProfileApiView.as_view(), name='profile'),
]
