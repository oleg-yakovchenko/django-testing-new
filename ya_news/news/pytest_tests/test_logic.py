"""Тесты бизнес-логики комментариев YaNews."""

from http import HTTPStatus

import pytest

from news.models import Comment

pytestmark = pytest.mark.django_db

BAD_WORD = 'редиска'
MODERATION_ERROR = 'Не ругайтесь!'


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
    Comment.objects.all().delete()

    response = author_client.post(
        news_detail_url, {'text': 'Новый комментарий'},
    )

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == 'Новый комментарий'
    assert comment.author == author
    assert comment.news == news


def test_create_redirects_to_news_comments_anchor(
    author_client, news_detail_url, news_detail_url_with_anchor,
):
    """После успешного создания — редирект к якорю #comments."""
    response = author_client.post(
        news_detail_url, {'text': 'Новый'},
    )

    assert response.url == news_detail_url_with_anchor


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
    new_text = 'Изменённый текст'

    response = author_client.post(edit_comment_url, {'text': new_text})

    assert response.status_code == HTTPStatus.FOUND
    updated = Comment.objects.get(pk=comment.pk)
    assert updated.text == new_text
    assert updated.author_id == comment.author_id
    assert updated.news_id == comment.news_id


def test_edit_redirects_to_news_comments_anchor(
    author_client, edit_comment_url, news_detail_url_with_anchor,
):
    """После успешного редактирования — редирект к #comments."""
    response = author_client.post(
        edit_comment_url, {'text': 'Новый текст'},
    )

    assert response.url == news_detail_url_with_anchor


def test_author_can_delete_own_comment(
    author_client, comment, delete_comment_url,
):
    """Автор удаляет свой комментарий."""
    count_before = Comment.objects.count()

    response = author_client.post(delete_comment_url)

    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()
    assert Comment.objects.count() == count_before - 1


def test_delete_redirects_to_news_comments_anchor(
    author_client, delete_comment_url, news_detail_url_with_anchor,
):
    """После успешного удаления — редирект к #comments."""
    response = author_client.post(delete_comment_url)

    assert response.url == news_detail_url_with_anchor


@pytest.mark.parametrize(
    'reverse_url',
    ['edit_comment_url', 'delete_comment_url'],
    indirect=['reverse_url'],
)
def test_non_author_gets_404_and_data_unchanged(
    reader_client, comment, reverse_url,
):
    """Чужой получает 404, данные в БД не меняются."""
    count_before = Comment.objects.count()

    response = reader_client.post(reverse_url, {'text': 'Взлом'})

    assert response.status_code == HTTPStatus.NOT_FOUND
    saved = Comment.objects.get(pk=comment.pk)
    assert saved.text == comment.text
    assert saved.author_id == comment.author_id
    assert saved.news_id == comment.news_id
    assert Comment.objects.count() == count_before
