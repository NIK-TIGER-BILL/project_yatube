from io import BytesIO

import pytest
from PIL import Image
from django import forms
from django.core.files.base import File
from posts.models import Post


class TestNewView:

    @pytest.mark.django_db(transaction=True)
    def test_new_view_get(self, user_client):
        try:
            response = user_client.get('/new')
        except Exception as e:
            assert False, f'''Страница `/new` работает неправильно. Ошибка: `{e}`'''
        if response.status_code in (301, 302):
            response = user_client.get('/new/')
        assert response.status_code != 404, 'Страница `/new/` не найдена, проверьте этот адрес в *urls.py*'
        assert 'form' in response.context, 'Проверьте, что передали форму `form` в контекст страницы `/new/`'
        assert len(response.context['form'].fields) == 3, 'Проверьте, что в форме `form` на страницу `/new/` 3 поля'
        assert 'group' in response.context['form'].fields, \
            'Проверьте, что в форме `form` на странице `/new/` есть поле `group`'
        assert type(response.context['form'].fields['group']) == forms.models.ModelChoiceField, \
            'Проверьте, что в форме `form` на странице `/new/` поле `group` типа `ModelChoiceField`'
        assert not response.context['form'].fields['group'].required, \
            'Проверьте, что в форме `form` на странице `/new/` поле `group` не обязательно'

        assert 'text' in response.context['form'].fields, \
            'Проверьте, что в форме `form` на странице `/new/` есть поле `text`'
        assert type(response.context['form'].fields['text']) == forms.fields.CharField, \
            'Проверьте, что в форме `form` на странице `/new/` поле `text` типа `CharField`'
        assert response.context['form'].fields['text'].required, \
            'Проверьте, что в форме `form` на странице `/new/` поле `group` обязательно'

        assert 'image' in response.context['form'].fields, \
            'Проверьте, что в форме `form` на странице `/new/` есть поле `image`'
        assert type(response.context['form'].fields['image']) == forms.fields.ImageField, \
            'Проверьте, что в форме `form` на странице `/new/` поле `image` типа `ImageField`'

    @staticmethod
    def get_image_file(name, ext='png', size=(50, 50), color=(256, 0, 0)):
        file_obj = BytesIO()
        image = Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    @pytest.mark.django_db(transaction=True)
    def test_new_view_post(self, user_client, user, group):
        text = 'Проверка нового поста!'
        try:
            response = user_client.get('/new')
        except Exception as e:
            assert False, f'''Страница `/new` работает неправильно. Ошибка: `{e}`'''
        url = '/new/' if response.status_code in (301, 302) else '/new'

        image = self.get_image_file('image.png')
        response = user_client.post(url, data={'text': text, 'group': group.id, 'image': image})

        assert response.status_code in (301, 302), \
            'Проверьте, что со страницы `/new/` после создания поста перенаправляете на главную страницу'
        post = Post.objects.filter(author=user, text=text, group=group).first()
        assert post is not None, 'Проверьте, что вы сохранили новый пост при отправки формы на странице `/new/`'
        assert response.url == '/', 'Проверьте, что перенаправляете на главную страницу `/`'

        text = 'Проверка нового поста 2!'
        image = self.get_image_file('image2.png')
        response = user_client.post(url, data={'text': text, 'image': image})
        assert response.status_code in (301, 302), \
            'Проверьте, что со страницы `/new/` после создания поста перенаправляете на главную страницу'
        post = Post.objects.filter(author=user, text=text, group__isnull=True).first()
        assert post is not None, 'Проверьте, что вы сохранили новый пост при отправки формы на странице `/new/`'
        assert response.url == '/', 'Проверьте, что перенаправляете на главную страницу `/`'

        response = user_client.post(url)
        assert response.status_code == 200, \
            'Проверьте, что на странице `/new/` выводите ошибки при неправильной заполненной формы `form`'
