from django.test import Client, TestCase

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

    def test_home_url(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_group_url(self):
        """Страница /group/<slug:slug>/ доступна любому пользователю."""
        response = self.guest_client.get(f'/group/{PostsURLTests.group.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_url(self):
        """Страница /new доступна авторизованному пользователю."""
        response = self.authorized_client.get('/new/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url(self):
        """Страница /<username>/ доступна любому пользователю."""
        response = self.guest_client.get(f'/{PostsURLTests.test_user.username}/')
        self.assertEqual(response.status_code, 200)

    def test_profile_url(self):
        """Несуществующая страница возращает ошибку 404"""
        response = self.guest_client.get('/false_page/')
        self.assertEqual(response.status_code, 404)

    def test_detailed_post_url(self):
        """Страница /<username>/<post_id>/доступна
        любому пользователю."""
        response = self.guest_client.get(
            f'/{PostsURLTests.test_user.username}/{PostsURLTests.post.id}/')
        self.assertEqual(response.status_code, 200)

    def test_guest_edit_post_url(self):
        """Страница /<username>/<post_id>/edit/ не доступна
        любому пользователю."""
        response = self.guest_client.get(
            f'/test/{PostsURLTests.post.id}/edit/')
        self.assertNotEqual(response.status_code, 200)

    def test_any_author_edit_post_url(self):
        """Страница /<username>/<post_id>/edit/ не доступна
        не автору поста."""
        user = User.objects.create(username='test_user_2')
        authorized_client_2 = Client()
        authorized_client_2.force_login(user)
        response = authorized_client_2.get(
            f'/test/{PostsURLTests.post.id}/edit/')
        self.assertNotEqual(response.status_code, 200)

    def test_true_author_edit_post_url(self):
        """Страница /<username>/<post_id>/edit/ доступна
        автору поста."""
        response = self.authorized_client.get(
            f'/test/{PostsURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_new_post_url_redirect(self):
        """Страница /new/ перенаправит анонимного пользователя
        на страницу логина."""
        response = self.guest_client.get('/new/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/new/')

    def test_edit_post_url_redirect(self):
        """Страница /<username>/<post_id>/edit/ перенаправит
        анонимного пользователяна страницу логина."""
        response = self.guest_client.get(
            f'/test/{PostsURLTests.post.id}/edit/',
            follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next=/test/{PostsURLTests.post.id}/edit/')

    def test_edit_post_use_true_template(self):
        """Страница /<username>/<post_id>/edit/ использует нужный шаблон."""
        response = self.authorized_client.get(
            f'/test/{PostsURLTests.post.id}/edit/')
        self.assertTemplateUsed(response, 'new_post.html')

    def test_urls_use_true_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'index.html': '/',
            'new_post.html': '/new/',
            'group.html': f'/group/{PostsURLTests.group.slug}/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
