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
            author=cls.test_user,
        )
        cls.EDIT_POST_URL = reverse(
            'posts:post_edit', args=[USERNAME, cls.post.id])
        cls.POST_URL = reverse(
            'posts:post', args=[USERNAME, cls.post.id])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

    def test_create_post(self):
        """Валидная форма создает пост в Post."""
        posts_count = Post.objects.count()
        list_id = []
        for post in Post.objects.all():
            list_id.append(post.id)
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
        self.assertEqual(len(response.context['page']), posts_count + 1)
        for post in response.context['page']:
            if post.id not in list_id:
                break
        self.assertEqual(post.author, PostCreateFormTests.test_user)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, PostCreateFormTests.group)
        self.assertEqual(post.image, 'posts/small.gif')

    def test_new_and_edit_post_page_context(self):
        """Шаблон new_post и edit_post сформирован с правильным контекстом."""
        urls = [
            NEW_POST_URL,
            PostCreateFormTests.EDIT_POST_URL]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for value, expected in form_fields.items():
                    form_field = response.context['form'].fields.get(value)
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
            content=SMALL_GIF,
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
        edit_post = response.context['post']
        self.assertRedirects(response, PostCreateFormTests.POST_URL)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group, other_group)
        self.assertEqual(edit_post.image, 'posts/other_small.gif')
        self.assertEqual(edit_post.author, PostCreateFormTests.test_user)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_create_post(self):
        """Гость не может создать новый post."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст'}
        self.guest_client.post(NEW_POST_URL, data=form_data)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_edit_post(self):
        """Гость не может редактировать пост."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Отредактируемый текст'}
        self.guest_client.post(
            PostCreateFormTests.EDIT_POST_URL,
            data=form_data,
        )
        edit_post = Post.objects.get(id=PostCreateFormTests.post.id)
        self.assertEqual(edit_post, PostCreateFormTests.post)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_add_comment_context(self):
        """Шаблон add_comment сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            PostCreateFormTests.POST_URL)
        form_field = response.context['form'].fields.get('text')
        self.assertIsInstance(form_field, forms.fields.CharField)
