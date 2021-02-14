from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='test')
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user,
        )

    def setUp(self):
        self.guest_client = Client()

    # То работает, то нет, сам по себе. Так и не разберусь как это решить
    def test_pages_uses_correct_template(self):
        """Кэширование данных на главной странице работает корректно"""
        Post.objects.create(text='Второй пост', author=self.test_user)

        response = self.guest_client.get(reverse('posts:index'))
        context = response.context.get('page')[0].text

        self.assertNotEqual(context, 'Второй пост')
