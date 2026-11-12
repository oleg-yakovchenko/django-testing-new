"""Тесты бизнес-логики комментариев YaNews."""

from http import HTTPStatus

import pytest
from django.urls import reverse

from news.models import Comment

pytestmark = pytest.mark.django_db

BAD_WORD = 'редиска'
MODERATION_ERROR = 'Не ругайтесь!'
COMMENTS_ANCHOR = '#comments'


def test_anonymous_cannot_create_comment(client, news_detail_url):
    """Аноним не может создать комментарий — количество не меняется."""
    count_before = Comment.objects.count()

    response = client.post(news_detail_url, {'text': 'Текст'})

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == count_before


def test_authenticated_user_creates_exactly_one_comment(
    author_client, author, news, news_detail_url,
):
    """Авторизованный создаёт ровно один комментарий с нужными полями."""
    count_before = Comment.objects.count()

    response = author_client.post(
        news_detail_url, {'text': 'Новый комментарий'},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == count_before + 1
    comment = Comment.objects.get()
    assert comment.text == 'Новый комментарий'
    assert comment.author == author
    assert comment.news == news


def test_create_redirects_to_news_comments_anchor(
    author_client, news, news_detail_url,
):
    """После успешного создания — редирект к якорю #comments."""
    expected = reverse('news:detail', args=(news.pk,)) + COMMENTS_ANCHOR

    response = author_client.post(
        news_detail_url, {'text': 'Новый'},
    )

    assert response.url == expected


@pytest.mark.parametrize(
    'bad_text',
    [
        f'Ты {BAD_WORD}!',
        f'Вот {BAD_WORD.upper()}',
        f'{BAD_WORD.upper()} какой-то',
    ],
)
def test_bad_word_rejected(
    author_client, news_detail_url, bad_text,
):
    """Комментарий со стоп-словом не сохраняется, ошибка у поля text."""
    count_before = Comment.objects.count()

    response = author_client.post(news_detail_url, {'text': bad_text})

    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == count_before
    errors = response.context['form'].errors
    assert 'text' in errors
    assert MODERATION_ERROR in errors['text']


def test_author_edits_comment_preserving_author_and_news(
    author_client, comment, edit_comment_url,
):
    """Автор меняет текст, не меняя автора и новость."""
    original_author_id = comment.author_id
    original_news_id = comment.news_id
    new_text = 'Изменённый текст'

    response = author_client.post(edit_comment_url, {'text': new_text})

    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_text
    assert comment.author_id == original_author_id
    assert comment.news_id == original_news_id


def test_edit_redirects_to_news_comments_anchor(
    author_client, comment, edit_comment_url,
):
    """После успешного редактирования — редирект к #comments."""
    expected = (
        reverse('news:detail', args=(comment.news.pk,)) + COMMENTS_ANCHOR
    )

    response = author_client.post(edit_comment_url, {'text': 'Новый текст'})

    assert response.url == expected


def test_author_can_delete_own_comment(
    author_client, comment, delete_comment_url,
):
    """Автор удаляет свой комментарий."""
    response = author_client.post(delete_comment_url)

    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_delete_redirects_to_news_comments_anchor(
    author_client, comment, delete_comment_url,
):
    """После успешного удаления — редирект к #comments."""
    expected = (
        reverse('news:detail', args=(comment.news.pk,)) + COMMENTS_ANCHOR
    )

    response = author_client.post(delete_comment_url)

    assert response.url == expected


@pytest.mark.parametrize('action_name', ['news:edit', 'news:delete'])
def test_non_author_gets_404_and_data_unchanged(
    reader_client, comment, action_name,
):
    """Чужой получает 404, данные в БД не меняются."""
    original = {
        'text': comment.text,
        'author_id': comment.author_id,
        'news_id': comment.news_id,
    }
    url = reverse(action_name, args=(comment.pk,))

    response = reader_client.post(url, {'text': 'Взлом'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == original['text']
    assert comment.author_id == original['author_id']
    assert comment.news_id == original['news_id']
