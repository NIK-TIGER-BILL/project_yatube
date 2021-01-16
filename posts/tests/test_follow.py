from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Post, User


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user_alex = User.objects.create(username='test_alex')
        cls.test_user_nikita = User.objects.create(username='test_nikita')

        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user_alex,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user_nikita)

    def test_follow_unfollow(self):
        """Проверка подписки и отписки на пользователя"""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={
                        'username': TaskPagesTests.test_user_alex.username
                    }))
        follow = Follow.objects.get(user=TaskPagesTests.test_user_nikita)
        self.assertEqual(TaskPagesTests.test_user_alex, follow.author)

        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={
                        'username': TaskPagesTests.test_user_alex.username
                    }), follow=True)
        self.assertRaises(Follow.DoesNotExist,
                          Follow.objects.get,
                          user=TaskPagesTests.test_user_nikita)

    def test_view_post_followed_and_unfollowed_users(self):
        """Посты отображаются у подписанных людей и наоборот"""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={
                        'username': TaskPagesTests.test_user_alex.username
                    }))
        response_nikita = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        context_nikita = response_nikita.context.get('page')

        test_user_taya = User.objects.create(username='test_taya')
        authorized_client_taya = Client()
        authorized_client_taya.force_login(test_user_taya)
        response_taya = authorized_client_taya.get(
            reverse('posts:follow_index')
        )
        context_taya = response_taya.context.get('page')

        self.assertEqual(len(context_taya), 0)
        self.assertEqual(context_nikita[0].text, TaskPagesTests.post.text)
