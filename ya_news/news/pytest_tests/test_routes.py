"""Тесты маршрутов и прав доступа YaNews."""

from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'route_name',
    ['news:home', 'users:login', 'users:signup'],
)
def test_public_pages_available_to_anonymous(client, route_name):
    """Главная, вход и регистрация доступны анонимному пользователю."""
    response = client.get(reverse(route_name))
    assert response.status_code == HTTPStatus.OK


def test_news_detail_available_to_anonymous(client, news_detail_url):
    """Страница отдельной новости доступна анонимному пользователю."""
    response = client.get(news_detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('route_name', ['news:edit', 'news:delete'])
def test_edit_and_delete_available_to_author(
    author_client, comment, route_name,
):
    """Автор видит страницы редактирования и удаления своего комментария."""
    url = reverse(route_name, args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('route_name', ['news:edit', 'news:delete'])
def test_edit_and_delete_return_404_for_non_author(
    reader_client, comment, route_name,
):
    """Другой пользователь получает 404 при обращении к чужому комментарию."""
    url = reverse(route_name, args=(comment.pk,))
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('route_name', ['news:edit', 'news:delete'])
def test_edit_and_delete_redirect_anonymous_with_next(
    client, comment, route_name,
):
    """Аноним редиректится на вход, в next — исходный адрес."""
    url = reverse(route_name, args=(comment.pk,))
    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND

    login_path = reverse('users:login')
    parsed = urlparse(response.url)
    assert parsed.path == login_path
    next_values = parse_qs(parsed.query).get('next', [])
    assert next_values == [url]


def test_logout_via_post_clears_session(author_client):
    """Выход POST-запросом очищает сессию."""
    assert '_auth_user_id' in author_client.session

    url = reverse('users:logout')
    author_client.post(url)

    assert '_auth_user_id' not in author_client.session
