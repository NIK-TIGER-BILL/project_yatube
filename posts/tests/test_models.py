from django.test import TestCase

from posts.models import Group, Post, User


class TaskModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='test')
        Group.objects.create(
            title='Тестовое название группы',
            slug='test_group',
            description='Текстовое описание группы'
        )
        Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user
        )
        cls.post = Post.objects.last()
        cls.group = Group.objects.last()

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = TaskModelTest.post
        group = TaskModelTest.group
        field_verboses = {
            'post': {
                'text': 'Текст поста',
                'pub_date': 'date published'},

            'group': {
                'title': 'Заголовок',
                'slug': 'Слаг',
                'description': 'Описание группы'},
        }
        for value, expected in field_verboses['post'].items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)
        for value, expected in field_verboses['group'].items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = TaskModelTest.post
        group = TaskModelTest.group
        field_help_texts = {
            'post': {
                'text': 'Здесь напишите текст записи'},
            'group': {
                'title': 'Дайте краткое название группе',
                'slug': 'Укажите ключ адреса страницы группы',
                'description': 'Опишите группу'}
        }
        for value, expected in field_help_texts['post'].items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
        for value, expected in field_help_texts['group'].items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_str_name(self):
        post = TaskModelTest.post
        group = TaskModelTest.group
        expected_object_name_post = post.text[:15]
        self.assertEquals(expected_object_name_post, str(post))
        expected_object_name_group = group.title
        self.assertEquals(expected_object_name_group, str(group))
