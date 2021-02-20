import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

TEST_DIR = settings.BASE_DIR + '\\test_data'
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
             )

USERNAME = 'test'
GROUP_SLUG = 'test-group'
PAGE_500_URL = reverse('posts:500')
INDEX_URL = reverse('posts:index')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
GROUP_URL = reverse('posts:group_posts', kwargs={'slug': GROUP_SLUG})
NEW_POST_URL = reverse('posts:new_post')
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = TEST_DIR

        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.test_user = User.objects.create(username=USERNAME)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_user)
        cls.group = Group.objects.create(
            title='Заголовок',
            slug=GROUP_SLUG,
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user,
            group=cls.group,
            image=cls.image
        )
        cls.POST_URL = reverse('posts:post', kwargs={
            'username': USERNAME,
            'post_id': TaskPagesTests.post.id
        })
        cls.EDIT_POST_URL = reverse('posts:post_edit', kwargs={
            'username': USERNAME,
            'post_id': TaskPagesTests.post.id
        })

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = [
            ['misc/500.html', PAGE_500_URL],
            ['index.html', INDEX_URL],
            ['follow.html', FOLLOW_INDEX_URL],
            ['group.html', GROUP_URL],
            ['new_post.html', NEW_POST_URL],
            ['profile.html', PROFILE_URL],
            ['detailed_post.html', TaskPagesTests.POST_URL],
            ['new_post.html', TaskPagesTests.EDIT_POST_URL],
        ]
        for row in templates_page_names:
            with self.subTest(template=row[0]):
                response = self.authorized_client.get(row[1])
                self.assertTemplateUsed(response, row[0])

    def test_post_view_on_page(self):
        """Новый пост отображается на страницах index, group, profile"""
        urls_pages = [INDEX_URL, GROUP_URL, PROFILE_URL]
        expect_context = self.post
        for url in urls_pages:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(len(response.context['page']), 1)
                current_context = response.context.get('page')[0]
                self.assertEqual(current_context, expect_context)

    def test_new_post_view_detailed_post_page(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(TaskPagesTests.POST_URL)
        current_context = response.context.get('post')
        expect_context = self.post
        self.assertEqual(current_context, expect_context)
