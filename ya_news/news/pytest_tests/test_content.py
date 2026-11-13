"""Тесты содержимого страниц YaNews."""

import pytest

from news.forms import CommentForm

from .conftest import NEWS_ON_PAGE

pytestmark = pytest.mark.django_db


def test_home_page_news_limit(client, home_url, many_news):
    """На главной не больше лимита новостей."""
    response = client.get(home_url)

    assert response.context['object_list'].count() == NEWS_ON_PAGE


def test_home_page_news_ordered_newest_first(client, home_url, many_news):
    """Новости на главной — от самой свежей к самой старой."""
    response = client.get(home_url)

    dates = [item.date for item in response.context['object_list']]
    assert dates == sorted(dates, reverse=True)


def test_detail_page_comments_ordered_oldest_first(
    client, news_detail_url, comments_with_different_dates,
):
    """Комментарии на странице новости — от старых к новым."""
    response = client.get(news_detail_url)

    comments = list(response.context['object'].comment_set.all())
    created_dates = [comment.created for comment in comments]
    assert created_dates == sorted(created_dates)


def test_detail_page_has_form_for_authenticated(
    author_client, news_detail_url,
):
    """Авторизованный пользователь получает форму комментария."""
    response = author_client.get(news_detail_url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_detail_page_has_no_form_for_anonymous(
    client, news_detail_url,
):
    """Анонимный пользователь не получает форму комментария."""
    response = client.get(news_detail_url)

    assert response.context.get('form') is None
