from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

USERNAME = 'test'
GROUP_SLUG = 'test-slug'
URL_INDEX = reverse('posts:index')
URL_GROUP = reverse('posts:group_posts', kwargs={'slug': GROUP_SLUG})
URL_NEW_POST = reverse('posts:new_post')
URL_PROFILE = reverse('posts:profile', kwargs={'username': USERNAME})
URL_FALSE_PAGE = '/false_page/'
URL_LOGIN = reverse('login')


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='test',
            slug=GROUP_SLUG,
            description='test description',
        )
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user
        )
        cls.URL_POST = reverse('posts:post', kwargs={
            'username': USERNAME,
            'post_id': PostsURLTests.post.id
        })
        cls.URL_EDIT_POST = reverse('posts:post_edit', kwargs={
            'username': USERNAME,
            'post_id': PostsURLTests.post.id
        })

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
        urls = [URL_INDEX,
                URL_GROUP,
                URL_NEW_POST,
                URL_PROFILE,
                URL_FALSE_PAGE,
                PostsURLTests.URL_POST,
                PostsURLTests.URL_EDIT_POST,
                PostsURLTests.URL_EDIT_POST,
                PostsURLTests.URL_EDIT_POST]
        status_codes = [200, 200, 200, 200, 404, 200, 302, 302, 200]

        for (client, url, status_code) in zip(clients, urls, status_codes):
            with self.subTest(client=client, url=url, status_code=status_code):
                response = client.get(url)
                self.assertEqual(response.status_code, status_code)

    def test_urls_redirect(self):
        """URL перенаправляет пользователя на нужную старницу"""
        redirects_url_names = [URL_NEW_POST, PostsURLTests.URL_EDIT_POST]
        for url in redirects_url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, URL_LOGIN + '?next=' + url)
