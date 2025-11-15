from django.urls import path
from users import views
from users.apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path('user/', views.UserView.as_view(), name='user')
]