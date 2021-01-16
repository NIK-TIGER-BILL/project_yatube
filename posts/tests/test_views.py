import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.test_user = User.objects.create(username='test')
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user,
            group=cls.group,
            image=cls.image
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'index.html': reverse('posts:index'),
            'new_post.html': reverse('posts:new_post'),
            'group.html': (
                reverse('posts:group_posts',
                        kwargs={'slug': TaskPagesTests.group.slug})
            ),
        }

        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_len(self):
        """Новый пост отображается на странице index"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page']), 1)

    def test_group_page_len(self):
        """Новый пост отображается на странице group"""
        response = self.guest_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': TaskPagesTests.group.slug})
        )
        self.assertEqual(len(response.context['page']), 1)

    def test_profile_page_len(self):
        """Новый пост отображается на странице profile"""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={
                'username': TaskPagesTests.test_user.username})
        )
        self.assertEqual(len(response.context['page']), 1)

    def test_new_post_page_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={
                        'username': TaskPagesTests.test_user.username,
                        'post_id': TaskPagesTests.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post_view_index_page(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))

        current_context = response.context.get('page')[0]
        expect_context = self.post

        self.assertEqual(current_context, expect_context)

    def test_new_post_view_group_page(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_posts',
                    kwargs={'slug': TaskPagesTests.group.slug})
            )

        current_context = response.context.get('page')[0]
        expect_context = self.post

        self.assertEqual(current_context, expect_context)

    def test_new_post_view_profile_page(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': TaskPagesTests.test_user.username})
            )

        current_context = response.context.get('page')[0]
        expect_context = self.post

        self.assertEqual(current_context, expect_context)

    def test_new_post_view_detailed_post_page(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post',
                    kwargs={'username': TaskPagesTests.test_user.username,
                            'post_id': TaskPagesTests.post.id})
            )

        current_context = response.context.get('post')
        expect_context = self.post

        self.assertEqual(current_context, expect_context)
