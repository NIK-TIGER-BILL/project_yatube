import pytest
from django.core.paginator import Page, Paginator


class TestGroupPaginatorView:

    @pytest.mark.django_db(transaction=True)
    def test_group_paginator_view_get(self, client, post_with_group):
        try:
            response = client.get(f'/group/{post_with_group.group.slug}')
        except Exception as e:
            assert False, f'''Страница `/group/<slug>/` работает неправильно. Ошибка: `{e}`'''
        if response.status_code in (301, 302):
            response = client.get(f'/group/{post_with_group.group.slug}/')
        assert response.status_code != 404, 'Страница `/group/<slug>/` не найдена, проверьте этот адрес в *urls.py*'

        assert 'paginator' in response.context, \
            'Проверьте, что передали переменную `paginator` в контекст страницы `/group/<slug>/`'
        assert type(response.context['paginator']) == Paginator, \
            'Проверьте, что переменная `paginator` на странице `/group/<slug>/` типа `Paginator`'
        assert 'page' in response.context, \
            'Проверьте, что передали переменную `page` в контекст страницы `/group/<slug>/`'
        assert type(response.context['page']) == Page, \
            'Проверьте, что переменная `page` на странице `/group/<slug>/` типа `Page`'

    @pytest.mark.django_db(transaction=True)
    def test_index_paginator_view_get(self, client, post_with_group):
        response = client.get(f'/')
        assert response.status_code != 404, 'Страница `/` не найдена, проверьте этот адрес в *urls.py*'
        assert 'paginator' in response.context, \
            'Проверьте, что передали переменную `paginator` в контекст страницы `/`'
        assert type(response.context['paginator']) == Paginator, \
            'Проверьте, что переменная `paginator` на странице `/` типа `Paginator`'
        assert 'page' in response.context, \
            'Проверьте, что передали переменную `page` в контекст страницы `/`'
        assert type(response.context['page']) == Page, \
            'Проверьте, что переменная `page` на странице `/` типа `Page`'
