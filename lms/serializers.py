from rest_framework.fields import SerializerMethodField
from rest_framework import serializers

from lms.models import Course, Lesson, Subscription
from lms.validators import validate_video_url


class CourseSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"

    def get_is_subscribed(self, obj):
        request = self.context.get("request")

        if not request or request.user.is_anonymous:
            return False

        user = request.user

        return Subscription.objects.filter(
            user=user,
            course=obj
        ).exists()


class LessonSerializer(serializers.ModelSerializer):
    video_link = serializers.URLField(validators=[validate_video_url])
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    class Meta:
        model = Course
        fields = ("name", "description", "lessons_count", "lessons",)
