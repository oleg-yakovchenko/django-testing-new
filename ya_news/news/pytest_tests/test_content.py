"""Тесты содержимого страниц YaNews."""

from datetime import date

import pytest

from news.forms import CommentForm
from news.models import News

pytestmark = pytest.mark.django_db

NEWS_LIMIT = 10


def test_home_page_news_limit(client, home_url, many_news):
    """На главной не больше 10 новостей."""
    response = client.get(home_url)

    assert len(response.context['object_list']) == NEWS_LIMIT


def test_home_page_news_ordered_newest_first(client, home_url):
    """Новости на главной — от самой свежей к самой старой."""
    old = News.objects.create(
        title='Старая', text='...', date=date(2024, 1, 1),
    )
    mid = News.objects.create(
        title='Средняя', text='...', date=date(2024, 6, 1),
    )
    new = News.objects.create(
        title='Новая', text='...', date=date(2024, 12, 1),
    )

    response = client.get(home_url)

    dates = [item.date for item in response.context['object_list']]
    assert dates == [new.date, mid.date, old.date]


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

    assert isinstance(response.context.get('form'), CommentForm)


def test_detail_page_has_no_form_for_anonymous(
    client, news_detail_url,
):
    """Анонимный пользователь не получает форму комментария."""
    response = client.get(news_detail_url)

    assert response.context.get('form') is None
