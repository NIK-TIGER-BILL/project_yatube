from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Post, User

USERNAME = 'test'


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username=USERNAME)
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user,
        )
        cls.ADD_COMMENT_URL = reverse('posts:add_comment',
                                      args=[USERNAME, cls.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

    def test_authorized_client_comment(self):
        """Авторизированный пользователь может комментировать пост"""
        text_comment = 'Тестовый комментарий'
        self.authorized_client.post(TaskPagesTests.ADD_COMMENT_URL,
                                    data={'text': text_comment}
                                    )
        comment = Comment.objects.filter(post=TaskPagesTests.post).last()
        self.assertEqual(comment.text, text_comment)
        self.assertEqual(comment.post, TaskPagesTests.post)
        self.assertEqual(comment.author, TaskPagesTests.test_user)

    def test_guest_client_comment_redirect_login(self):
        """Гость не может создать комментарий"""
        count_comments = Comment.objects.count()
        self.guest_client.post(TaskPagesTests.ADD_COMMENT_URL)
        self.assertEqual(count_comments, Comment.objects.count())
