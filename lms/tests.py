from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status

from lms.models import Lesson, Course, Subscription

User = get_user_model()


class LessonSubscriptionTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email="user@test.com", password="123456")
        self.moderator = User.objects.create_user(email="moder@test.com", password="123456")
        self.owner = User.objects.create_user(email="owner@test.com", password="123456")

        moderators_group = Group.objects.create(name="moders")
        self.moderator.groups.add(moderators_group)

        self.course = Course.objects.create(
            name="Python Developer",
            owner=self.owner
        )

        self.lesson = Lesson.objects.create(
            name="Введение",
            course=self.course,
            owner=self.owner
        )

        self.lesson_list_url = reverse("lms:lesson_list")
        self.lesson_create_url = reverse("lms:lesson_create")
        self.lesson_detail_url = reverse("lms:lesson_retrieve", args=(self.lesson.id,))
        self.lesson_update_url = reverse("lms:lesson_update", args=(self.lesson.id,))

        self.subscription_url = reverse("lms:subscription")
        self.course_detail_url = reverse("lms:course-detail", args=(self.course.id,))

    #  Анонимный пользователь
    def test_anonymous_cannot_create_lesson(self):
        response = self.client.post(self.lesson_create_url, {
            "name": "Новый урок",
            "course": self.course.id
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    #  Модератор
    def test_moderator_can_update_lesson(self):
        self.client.force_authenticate(self.moderator)

        response = self.client.patch(self.lesson_update_url, {
            "name": "Обновлённый урок"
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Обновлённый урок")

    #  Проверка, что урок отображается в списке
    def test_lesson_list(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.lesson_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    #  Пользователь может подписаться
    def test_user_can_subscribe(self):
        self.client.force_authenticate(self.user)

        response = self.client.post(self.subscription_url, {
            "course": self.course.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    #  Пользователь может отписаться
    def test_user_can_unsubscribe(self):
        self.client.force_authenticate(self.user)
        Subscription.objects.create(user=self.user, course=self.course)

        response = self.client.post(self.subscription_url, {
            "course": self.course.id
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    #  Анонимный пользователь не может подписываться
    def test_anonymous_cannot_subscribe(self):
        response = self.client.post(self.subscription_url, {
            "course": self.course.id
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
