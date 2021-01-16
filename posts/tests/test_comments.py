from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Post, User


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
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

    def test_authorized_client_comment(self):
        """Авторизированный пользователь может комментиовать пост"""
        self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'username': TaskPagesTests.test_user.username,
                            'post_id': TaskPagesTests.post.id},),
            data={'text': 'Тестовый комментарий'}
        )
        comment = Comment.objects.get(author=TaskPagesTests.test_user)
        self.assertEqual(comment.text, 'Тестовый комментарий')

    def test_guest_client_comment_redirect_login(self):
        """Гостя переводит на авторизацию при комментировании"""
        response = self.guest_client.get(
            reverse('posts:add_comment',
                    kwargs={'username': TaskPagesTests.test_user.username,
                            'post_id': TaskPagesTests.post.id},), follow=True)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/{TaskPagesTests.test_user.username}/'
            f'{TaskPagesTests.post.id}/comment')
