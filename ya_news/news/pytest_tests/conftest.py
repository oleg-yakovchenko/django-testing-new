"""Общие фикстуры для тестов YaNews."""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()

NEWS_ON_PAGE = 10
COMMENTS_COUNT = 3


@pytest.fixture
def author(db):
    """Пользователь — автор комментария."""
    return User.objects.create_user(
        username='author', password='pass12345'
    )


@pytest.fixture
def reader(db):
    """Другой пользователь, не автор."""
    return User.objects.create_user(
        username='reader', password='pass12345'
    )


@pytest.fixture
def author_client(db, author):
    """Клиент, авторизованный как автор."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(db, reader):
    """Клиент, авторизованный как другой пользователь."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    """Одна новость."""
    return News.objects.create(
        title='Тестовая новость', text='Текст новости'
    )


@pytest.fixture
def comment(db, news, author):
    """Комментарий автора к новости."""
    return Comment.objects.create(
        news=news, author=author, text='Тестовый комментарий'
    )


@pytest.fixture
def many_news(db):
    """Новостей на одну больше лимита на главной."""
    News.objects.bulk_create(
        News(
            title=f'Новость {i}',
            text=f'Текст {i}',
            date=date(2024, 1, 1) + timedelta(days=i),
        )
        for i in range(NEWS_ON_PAGE + 1)
    )


@pytest.fixture
def comments_with_different_dates(db, news, author):
    """Комментарии с разным временем создания."""
    comments = [
        Comment.objects.create(
            news=news, author=author, text=f'Комментарий {i}'
        )
        for i in range(COMMENTS_COUNT)
    ]
    now = timezone.now()
    for i, item in enumerate(comments):
        Comment.objects.filter(pk=item.pk).update(
            created=now + timedelta(minutes=i)
        )


@pytest.fixture
def home_url():
    """Адрес главной страницы."""
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    """Адрес страницы новости."""
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def edit_comment_url(comment):
    """Адрес редактирования комментария."""
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def delete_comment_url(comment):
    """Адрес удаления комментария."""
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def news_detail_url_with_anchor(news):
    """Адрес страницы новости с якорем #comments."""
    return reverse('news:detail', args=(news.pk,)) + '#comments'


@pytest.fixture
def login_url():
    """Адрес страницы входа."""
    return reverse('users:login')


@pytest.fixture
def signup_url():
    """Адрес страницы регистрации."""
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    """Адрес страницы выхода."""
    return reverse('users:logout')


@pytest.fixture
def reverse_url(request):
    """URL по имени фикстуры из параметризации."""
    return request.getfixturevalue(request.param)


@pytest.fixture
def parametrized_client(request):
    """Клиент по имени фикстуры из параметризации."""
    return request.getfixturevalue(request.param)
