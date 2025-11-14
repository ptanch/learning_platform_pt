from django.urls import path
from rest_framework.routers import SimpleRouter

from lms.views import CourseViewSet
from lms.views import (
    LessonCreateApiView,
    LessonListApiView,
    LessonUpdateApiView,
    LessonRetrieveApiView,
    LessonDestroyApiView
)
from lms.apps import LmsConfig

app_name = LmsConfig.name

router = SimpleRouter()
router.register("", CourseViewSet)


urlpatterns = [
    path("lesson/", LessonListApiView.as_view(), name="lesson_list"),
    path("lesson/<int:pk>/", LessonRetrieveApiView.as_view(), name="lesson_retrieve"),
    path("lesson/create/", LessonCreateApiView.as_view(), name="lesson_create"),
    path("lesson/<int:pk>/delete/", LessonDestroyApiView.as_view(), name="lesson_delete"),
    path("lesson/<int:pk>/update/", LessonUpdateApiView.as_view(), name="lesson_update"),
]

urlpatterns += router.urls
