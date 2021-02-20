import shutil

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

TEST_DIR = settings.BASE_DIR + '\\test_data'
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')

OTHER_SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                   b'\x01\x00\x80\x00\x00\x00\x00\x00'
                   b'\x00\x00\xFF\x21\xF9\x04\x00\x00'
                   b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                   b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                   b'\x0A\x00\x3B')
USERNAME = 'test'
INDEX_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:new_post')


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = TEST_DIR
        cls.form = PostForm()
        cls.test_user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title='Заголовок',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=User.objects.get(id=cls.test_user.id),
        )
        cls.EDIT_POST_URL = reverse(
            'posts:post_edit', kwargs={
                'username': USERNAME, 'post_id': PostCreateFormTests.post.id})
        cls.POST_URL = reverse(
            'posts:post', kwargs={
                'username': USERNAME, 'post_id': PostCreateFormTests.post.id})

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

    def test_create_post(self):
        """Валидная форма создает пост в Post."""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'group': PostCreateFormTests.group.pk,
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, INDEX_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateFormTests.test_user,
                text=form_data['text'],
                group=PostCreateFormTests.group,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post_page_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        urls = [
            NEW_POST_URL,
            PostCreateFormTests.EDIT_POST_URL]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for url in urls:
            response = self.authorized_client.get(url)
            for value, expected in form_fields.items():
                with self.subTest(url=url, value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_edit_post(self):
        """Валидная форма редактирует пост в Post."""
        posts_count = Post.objects.count()
        other_group = Group.objects.create(
            title='Заголовок группы',
            slug='test-slug_other',
            description='Другое тестовое описание',
        )
        uploaded = SimpleUploadedFile(
            name='other_small.gif',
            content=OTHER_SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'group': other_group.pk,
            'text': 'Отредактируемый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            PostCreateFormTests.EDIT_POST_URL,
            data=form_data,
            follow=True
        )
        edit_post = response.context.get('post')
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group, other_group)
        self.assertEqual(edit_post.image, 'posts/other_small.gif')
        self.assertRedirects(response, PostCreateFormTests.POST_URL)
        self.assertEqual(Post.objects.count(), posts_count)
