from io import BytesIO

import pytest
from django import forms
from django.contrib.auth import get_user_model
from django.core.files.base import File
from django.db.models.query import QuerySet
from PIL import Image

from posts.models import Post


def get_field_context(context, field_type):
    for field in context.keys():
        if field not in ('user', 'request') and type(context[field]) == field_type:
            return context[field]
    return


class TestPostView:

    @pytest.mark.django_db(transaction=True)
    def test_post_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/{post_with_group.author.username}/{post_with_group.id}')
        except Exception as e:
            assert False, f'''Страница `/<username>/<post_id>/` работает неправильно. Ошибка: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/{post_with_group.author.username}/{post_with_group.id}/')
        assert response.status_code != 404, \
            'Страница `/<username>/<post_id>/` не найдена, проверьте этот адрес в *urls.py*'

        profile_context = get_field_context(response.context, get_user_model())
        assert profile_context is not None, \
            'Проверьте, что передали автора в контекст страницы `/<username>/<post_id>/`'

        post_context = get_field_context(response.context, Post)
        assert post_context is not None, \
            'Проверьте, что передали статью в контекст страницы `/<username>/<post_id>/` типа `Post`'

        try:
            from posts.forms import CommentForm
        except ImportError:
            assert False, 'Не найдена форма CommentForm в posts.form'

        comment_form_context = get_field_context(response.context, CommentForm)
        assert comment_form_context is not None, \
            'Проверьте, что передали форму комментария в контекст страницы `/<username>/<post_id>/` типа `CommentForm`'
        assert len(comment_form_context.fields) == 1, \
            'Проверьте, что форма комментария в контекстке страницы `/<username>/<post_id>/` состоит из одного поля'
        assert 'text' in comment_form_context.fields, \
            'Проверьте, что форма комментария в контекстке страницы `/<username>/<post_id>/` содержится поле `text`'
        assert type(comment_form_context.fields['text']) == forms.fields.CharField, \
            'Проверьте, что форма комментария в контекстке страницы `/<username>/<post_id>/` содержится поле `text` типа `CharField`'

        comment_context = get_field_context(response.context, QuerySet)
        assert comment_context is not None, \
            'Проверьте, что передали список комментариев в контекст страницы `/<username>/<post_id>/` типа `QuerySet`'


class TestPostEditView:

    @pytest.mark.django_db(transaction=True)
    def test_post_edit_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/{post_with_group.author.username}/{post_with_group.id}/edit')
        except Exception as e:
            assert False, f'''Страница `/<username>/<post_id>/edit/` работает неправильно. Ошибка: `{e}`'''
        if response.status_code in (301, 302) and not response.url.startswith(f'/{post_with_group.author.username}/{post_with_group.id}'):
            response = client.get(f'/{post_with_group.author.username}/{post_with_group.id}/edit/')
        assert response.status_code != 404, \
            'Страница `/<username>/<post_id>/edit/` не найдена, проверьте этот адрес в *urls.py*'

        assert response.status_code in (301, 302), \
            'Проверьте, что вы переадресуете пользователя со страницы `/<username>/<post_id>/edit/` на страницу поста, если он не автор'

    @pytest.mark.django_db(transaction=True)
    def test_post_edit_view_author_get(self, user_client, post_with_group):
        try:
            response = user_client.get(f'/{post_with_group.author.username}/{post_with_group.id}/edit')
        except Exception as e:
            assert False, f'''Страница `/<username>/<post_id>/edit/` работает неправильно. Ошибка: `{e}`'''
        if response.status_code in (301, 302):
            response = user_client.get(f'/{post_with_group.author.username}/{post_with_group.id}/edit/')
        assert response.status_code != 404, \
            'Страница `/<username>/<post_id>/edit/` не найдена, проверьте этот адрес в *urls.py*'

        post_context = get_field_context(response.context, Post)
        assert post_context is not None, \
            'Проверьте, что передали статью в контекст страницы `/<username>/<post_id>/edit/` типа `Post`'

        assert 'form' in response.context, \
            'Проверьте, что передали форму `form` в контекст страницы `/<username>/<post_id>/edit/`'
        assert len(response.context['form'].fields) == 3, \
            'Проверьте, что в форме `form` на страницу `/<username>/<post_id>/edit/` 3 поля'
        assert 'group' in response.context['form'].fields, \
            'Проверьте, что в форме `form` на странице `/<username>/<post_id>/edit/` есть поле `group`'
        assert type(response.context['form'].fields['group']) == forms.models.ModelChoiceField, \
            'Проверьте, что в форме `form` на странице `/<username>/<post_id>/edit/` поле `group` типа `ModelChoiceField`'
        assert not response.context['form'].fields['group'].required, \
            'Проверьте, что в форме `form` на странице `/<username>/<post_id>/edit/` поле `group` не обязательно'

        assert 'text' in response.context['form'].fields, \
            'Проверьте, что в форме `form` на странице `/<username>/<post_id>/edit/` есть поле `text`'
        assert type(response.context['form'].fields['text']) == forms.fields.CharField, \
            'Проверьте, что в форме `form` на странице `/<username>/<post_id>/edit/` поле `text` типа `CharField`'
        assert response.context['form'].fields['text'].required, \
            'Проверьте, что в форме `form` на странице `/<username>/<post_id>/edit/` поле `group` обязательно'

        assert 'image' in response.context['form'].fields, \
            'Проверьте, что в форме `form` на странице `/<username>/<post_id>/edit/` есть поле `image`'
        assert type(response.context['form'].fields['image']) == forms.fields.ImageField, \
            'Проверьте, что в форме `form` на странице `/<username>/<post_id>/edit/` поле `image` типа `ImageField`'

    @staticmethod
    def get_image_file(name, ext='png', size=(50, 50), color=(256, 0, 0)):
        file_obj = BytesIO()
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    @pytest.mark.django_db(transaction=True)
    def test_post_edit_view_author_post(self, user_client, post_with_group):
        text = 'Проверка изменения поста!'
        try:
            response = user_client.get(f'/{post_with_group.author.username}/{post_with_group.id}/edit')
        except Exception as e:
            assert False, f'''Страница `/<username>/<post_id>/edit/` работает неправильно. Ошибка: `{e}`'''
        url = f'/{post_with_group.author.username}/{post_with_group.id}/edit/' if response.status_code in (301, 302) else f'/{post_with_group.author.username}/{post_with_group.id}/edit'

        image = self.get_image_file('image2.png')
        response = user_client.post(url, data={'text': text, 'group': post_with_group.group_id, 'image': image})

        assert response.status_code in (301, 302), \
            'Проверьте, что со страницы `/<username>/<post_id>/edit/` после создания поста перенаправляете на страницу поста'
        post = Post.objects.filter(author=post_with_group.author, text=text, group=post_with_group.group).first()
        assert post is not None, \
            'Проверьте, что вы изминили пост при отправки формы на странице `/<username>/<post_id>/edit/`'
        assert response.url.startswith(f'/{post_with_group.author.username}/{post_with_group.id}'),\
            'Проверьте, что перенаправляете на страницу поста `/<username>/<post_id>/`'
