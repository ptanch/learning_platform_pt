from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from users.models import User
from users.serializers import UserSerializer


class UserCreateApiView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserUpdateApiView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileApiView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
