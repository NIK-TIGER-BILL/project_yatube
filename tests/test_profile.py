import pytest
from django.contrib.auth import get_user_model
from django.core.paginator import Page, Paginator


def get_field_context(context, field_type):
    for field in context.keys():
        if field not in ('user', 'request') and type(context[field]) == field_type:
            return context[field]
    return


class TestProfileView:

    @pytest.mark.django_db(transaction=True)
    def test_profile_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/{post_with_group.author.username}')
        except Exception as e:
            assert False, f'''Страница `/<username>/` работает неправильно. Ошибка: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/{post_with_group.author.username}/')
        assert response.status_code != 404, 'Страница `/<username>/` не найдена, проверьте этот адрес в *urls.py*'

        profile_context = get_field_context(response.context, get_user_model())
        assert profile_context is not None, 'Проверьте, что передали автора в контекст страницы `/<username>/`'

        page_context = get_field_context(response.context, Page)
        assert page_context is not None, \
            'Проверьте, что передали статьи автора в контекст страницы `/<username>/` типа `Page`'
        assert len(page_context.object_list) == 1, \
            'Проверьте, что правильные статьи автора в контекст страницы `/<username>/`'

        paginator_context = get_field_context(response.context, Paginator)
        assert paginator_context is not None, \
            'Проверьте, что передали паджинатор в контекст страницы `/<username>/` типа `Paginator`'

        new_user = get_user_model()(username='new_user_87123478')
        new_user.save()
        try:
            new_response = client.get(f'/{new_user.username}')
        except Exception as e:
            assert False, f'''Страница `/<username>/` работает неправильно. Ошибка: `{e}`'''
        if new_response.status_code in (301, 302):
            new_response = client.get(f'/{new_user.username}/')

        page_context = get_field_context(new_response.context, Page)
        assert page_context is not None, \
            'Проверьте, что передали статьи автора в контекст страницы `/<username>/` типа `Page`'
        assert len(page_context.object_list) == 0, \
            'Проверьте, что правильные статьи автора в контекст страницы `/<username>/`'
