from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='test')
        cls.group = Group.objects.create(
            title="test",
            slug="test-slug",
            description="test description",
        )
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

    def test_urls(self):
        """Страницы сайта выдают верный статус код"""
        user = User.objects.create(username='test_user_2')
        authorized_client_2 = Client()
        authorized_client_2.force_login(user)
        clients = [self.guest_client, self.guest_client,
                   self.authorized_client, self.guest_client,
                   self.guest_client, self.guest_client, self.guest_client,
                   authorized_client_2, self.authorized_client]
        urls = [reverse('posts:index'),
                reverse('posts:group_posts',
                        kwargs={'slug': PostsURLTests.group.slug}),
                reverse('posts:new_post'),
                reverse('posts:profile', kwargs={
                    'username': PostsURLTests.test_user.username}),
                '/false_page/',
                reverse('posts:post', kwargs={
                    'username': PostsURLTests.test_user.username,
                    'post_id': PostsURLTests.post.id
                }),
                reverse('posts:post_edit', kwargs={
                    'username': PostsURLTests.test_user.username,
                    'post_id': PostsURLTests.post.id
                }),
                reverse('posts:post_edit', kwargs={
                    'username': PostsURLTests.test_user.username,
                    'post_id': PostsURLTests.post.id
                }),
                reverse('posts:post_edit', kwargs={
                    'username': PostsURLTests.test_user.username,
                    'post_id': PostsURLTests.post.id
                })]
        status_codes = [200, 200, 200, 200, 404, 200, 302, 302, 200]

        for (client, url, status_code) in zip(clients, urls, status_codes):
            with self.subTest(client=client, url=url, status_code=status_code):
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_redirect(self):
        """URL перенаправляет пользователя на нужную старницу"""
        redirects_url_names = {
            reverse('login'): reverse('posts:new_post'),
            reverse('login'): reverse('posts:post_edit', kwargs={
                'username': PostsURLTests.test_user.username,
                'post_id': PostsURLTests.post.id
            }),
        }
        for redirect, url in redirects_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirect + '?next=' + url)
