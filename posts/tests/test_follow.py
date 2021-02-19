from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post, User

USERNAME_ALEX = 'test_alex'
USERNAME_NIKITA = 'test_nikita'
URL_FOLLOW_TO_ALEX = reverse('posts:profile_follow',
                             kwargs={'username': USERNAME_ALEX})
URL_UNFOLLOW_TO_ALEX = reverse('posts:profile_unfollow',
                               kwargs={'username': USERNAME_ALEX})
URL_FOLLOW_INDEX = reverse('posts:follow_index')


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user_alex = User.objects.create(username=USERNAME_ALEX)
        cls.test_user_nikita = User.objects.create(username=USERNAME_NIKITA)
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user_alex,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user_nikita)

    def test_follow(self):
        """Проверка подписки на пользователя"""
        self.authorized_client.get(URL_FOLLOW_TO_ALEX)
        follow = Follow.objects.get(user=TaskPagesTests.test_user_nikita)
        self.assertEqual(TaskPagesTests.test_user_alex, follow.author)

    def test_unfollow(self):
        """Проверка отписки от пользователя"""
        Follow.objects.create(user=TaskPagesTests.test_user_nikita,
                              author=TaskPagesTests.test_user_alex)
        self.authorized_client.get(URL_UNFOLLOW_TO_ALEX, follow=True)
        self.assertFalse(Follow.objects.filter(
            user=TaskPagesTests.test_user_nikita,
            author=TaskPagesTests.test_user_alex).exists())

    def test_view_post_followed_and_unfollowed_users(self):
        """Посты отображаются у подписанных людей"""
        self.authorized_client.get(URL_FOLLOW_TO_ALEX)
        response_nikita = self.authorized_client.get(URL_FOLLOW_INDEX)
        context_nikita = response_nikita.context.get('page')
        test_user_taya = User.objects.create(username='test_taya')
        authorized_client_taya = Client()
        authorized_client_taya.force_login(test_user_taya)
        response_taya = authorized_client_taya.get(URL_FOLLOW_INDEX)
        context_taya = response_taya.context.get('page')
        self.assertEqual(len(context_taya), 0)
        self.assertEqual(context_nikita[0].text, TaskPagesTests.post.text)
