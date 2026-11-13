"""Тесты маршрутов и прав доступа YaNews."""

from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    [
        ('home_url', 'client', HTTPStatus.OK),
        ('login_url', 'client', HTTPStatus.OK),
        ('signup_url', 'client', HTTPStatus.OK),
        ('news_detail_url', 'client', HTTPStatus.OK),
        ('edit_comment_url', 'author_client', HTTPStatus.OK),
        ('delete_comment_url', 'author_client', HTTPStatus.OK),
        ('edit_comment_url', 'reader_client', HTTPStatus.NOT_FOUND),
        ('delete_comment_url', 'reader_client', HTTPStatus.NOT_FOUND),
    ],
    indirect=['reverse_url', 'parametrized_client'],
)
def test_get_status_codes(reverse_url, parametrized_client, status):
    """GET-статусы страниц соответствуют ожиданиям."""
    response = parametrized_client.get(reverse_url)

    assert response.status_code == status


def test_logout_via_post(author_client, logout_url):
    """Выход POST-запросом очищает сессию."""
    assert '_auth_user_id' in author_client.session

    author_client.post(logout_url)

    assert '_auth_user_id' not in author_client.session


@pytest.mark.parametrize(
    'reverse_url',
    ['edit_comment_url', 'delete_comment_url'],
    indirect=['reverse_url'],
)
def test_anonymous_redirects_to_login_with_next(
    client, reverse_url, login_url,
):
    """Аноним редиректится на вход, в next — исходный адрес."""
    response = client.get(reverse_url)

    assert response.status_code == HTTPStatus.FOUND

    parsed = urlparse(response.url)
    assert parsed.path == login_url
    next_values = parse_qs(parsed.query).get('next', [])
    assert next_values == [reverse_url]
