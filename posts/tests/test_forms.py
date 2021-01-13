import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        cls.form = PostForm()
        cls.test_user = User.objects.create(username='test')
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=User.objects.get(id=cls.test_user.id),
        )

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

        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:new_post'),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, '/')
        self.assertEqual(Post.objects.count(), posts_count+1)

    def test_edit_post(self):
        """Валидная форма редактирует пост в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактируемый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'username': PostCreateFormTests.test_user.username,
                'post_id': PostCreateFormTests.post.id
            }),
            data=form_data,
            follow=True
        )
        post_after = Post.objects.last()

        self.assertEqual(post_after.text, form_data['text'])
        self.assertRedirects(response,
                             f'/{self.test_user.username}/{self.post.id}/')
        self.assertEqual(Post.objects.count(), posts_count)

