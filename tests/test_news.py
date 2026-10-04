import pytest
from domain.news import News

# Тест успешного создания доменного объекта Новости
def test_news_creation_valid():
    news = News(title="Начало сессии", content="Расписание экзамнов опубликовано")
    assert news.title == "Начало сессии"
    assert news.is_valid_title() is True

# Тест проверки слишком короткого заголовка
def test_news_invalid_title():
    news = News(title="А ", content="Описание новости")
    assert news.is_valid_title() is False

# Тест автоматической простановки даты
def test_news_set_date_automatically():
    news = News(title="Конференция", content="Приглашаем всех желающих")
    assert news.date is None
    news.set_current_date()
    assert news.date is not None