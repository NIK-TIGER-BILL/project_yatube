from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post, User

ALEX_USERNAME = 'test_alex'
NIKITA_USERNAME = 'test_nikita'
FOLLOW_TO_ALEX_URL = reverse('posts:profile_follow', args=[ALEX_USERNAME])
UNFOLLOW_TO_ALEX_URL = reverse('posts:profile_unfollow', args=[ALEX_USERNAME])
FOLLOW_INDEX_URL = reverse('posts:follow_index')


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user_alex = User.objects.create(username=ALEX_USERNAME)
        cls.test_user_nikita = User.objects.create(username=NIKITA_USERNAME)
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user_alex,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user_nikita)

    def test_follow(self):
        """Проверка подписки на пользователя"""
        self.authorized_client.get(FOLLOW_TO_ALEX_URL)
        self.assertTrue(Follow.objects.filter(
            user=TaskPagesTests.test_user_nikita,
            author=TaskPagesTests.test_user_alex).exists())

    def test_unfollow(self):
        """Проверка отписки от пользователя"""
        Follow.objects.create(user=TaskPagesTests.test_user_nikita,
                              author=TaskPagesTests.test_user_alex)
        self.authorized_client.get(UNFOLLOW_TO_ALEX_URL, follow=True)
        self.assertFalse(Follow.objects.filter(
            user=TaskPagesTests.test_user_nikita,
            author=TaskPagesTests.test_user_alex).exists())

    def test_view_post_followed_users(self):
        """Посты отображаются у подписанных людей"""
        Follow.objects.create(user=TaskPagesTests.test_user_nikita,
                              author=TaskPagesTests.test_user_alex)
        response_nikita = self.authorized_client.get(FOLLOW_INDEX_URL)
        context_nikita = response_nikita.context['page']
        self.assertIn(TaskPagesTests.post, context_nikita)

    def test_do_not_view_post_unfollowed_users(self):
        """Посты неотображаются у неподписанных людей"""
        authorized_client_alex = Client()
        authorized_client_alex.force_login(self.test_user_nikita)
        response_alex = authorized_client_alex.get(FOLLOW_INDEX_URL)
        self.assertNotIn(TaskPagesTests.post, response_alex.context['page'])
