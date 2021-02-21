from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

USERNAME = 'test'
OTHER_USERNAME = 'other'
GROUP_SLUG = 'test-slug'
INDEX_URL = reverse('posts:index')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
GROUP_URL = reverse('posts:group_posts', args=[GROUP_SLUG])
NEW_POST_URL = reverse('posts:new_post')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
FALSE_PAGE_URL = '/false_page/'
LOGIN_URL = reverse('login')


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
        cls.POST_URL = reverse('posts:post', args=[USERNAME, cls.post.id])
        cls.EDIT_POST_URL = reverse('posts:post_edit',
                                    args=[USERNAME, cls.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

    def test_urls(self):
        """Страницы сайта выдают верный статус код"""
        user = User.objects.create(username='test_user_2')
        authorized_client_2 = Client()
        authorized_client_2.force_login(user)
        client_url_status = [
            [self.guest_client, INDEX_URL, 200],
            [self.authorized_client, FOLLOW_INDEX_URL, 200],
            [self.guest_client, FOLLOW_INDEX_URL, 302],
            [self.guest_client, GROUP_URL, 200],
            [self.authorized_client, NEW_POST_URL, 200],
            [self.guest_client, PROFILE_URL, 200],
            [self.guest_client, FALSE_PAGE_URL, 404],
            [self.guest_client, PostsURLTests.POST_URL, 200],
            [self.guest_client, PostsURLTests.EDIT_POST_URL, 302],
            [authorized_client_2, PostsURLTests.EDIT_POST_URL, 302],
            [self.authorized_client, PostsURLTests.EDIT_POST_URL, 200],
        ]
        for client, url, status_code in client_url_status:
            with self.subTest(client=client, url=url, status_code=status_code):
                self.assertEqual(client.get(url).status_code, status_code)

    def test_urls_redirect(self):
        """URL перенаправляет пользователя на нужную старницу"""
        other_test_user = User.objects.create(username=OTHER_USERNAME)
        other_client = Client()
        other_client.force_login(other_test_user)
        client_url_redirect = [
            [self.guest_client, NEW_POST_URL,
             f'{LOGIN_URL}?next={NEW_POST_URL}'],
            [self.guest_client, PostsURLTests.EDIT_POST_URL,
             f'{LOGIN_URL}?next={PostsURLTests.EDIT_POST_URL}'],
            [other_client, PostsURLTests.EDIT_POST_URL,
             PostsURLTests.POST_URL],
            [self.guest_client, FOLLOW_INDEX_URL,
             f'{LOGIN_URL}?next={FOLLOW_INDEX_URL}'],
        ]
        for client, url, redirect_url in client_url_redirect:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url, follow=True), redirect_url)
