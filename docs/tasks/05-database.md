# Задача 05. Интеграция с БД + миграции

**Ветка:** `feature/database` · **Зависимости:** фичи 01–04 (хотя бы одна)
**Инструменты:** SQLAlchemy 2.0, Alembic, SQLite/PostgreSQL, pytest + фикстуры

## Чему учимся
Заменять JSON-заглушки на настоящую БД, не меняя контракт API и тесты;
миграции, сессии, транзакции, изоляция тестов.

## Задача
Ввести слой БД так, чтобы **роуты и схемы не изменились** — меняется только
`api/app/services/*` и добавляется `api/app/db/`.

## План работы
1. Зависимости в `api/requirements.txt`: `sqlalchemy`, `alembic`, `psycopg[binary]`.
   В `requirements-dev.txt` — ничего нового (для тестов хватит SQLite).
2. `api/app/db/base.py` — `DeclarativeBase`; `api/app/db/session.py` — `engine`,
   `SessionLocal`, `get_session()` (зависимость FastAPI через `Depends`).
3. `api/app/db/models.py` — таблицы `teachers`, `news`, `lessons`, `publications`.
   Связи: `news.author_id -> teachers.id`, `publications` ↔ `teachers` (M2M).
4. Alembic: `alembic init api/alembic`, строка подключения из `core/config.py`
   (env `DATABASE_URL`, по умолчанию `sqlite:///./itis.db`).
5. Переписать сервисы на сессии БД. Сигнатуры вида `list_teachers(session, q=None)`.
6. **Тесты**: переопределить зависимость `get_session` на тестовую БД
   (`app.dependency_overrides`) — SQLite в памяти, `create_all` в фикстуре,
   откат после каждого теста. Существующие тесты (01–04) должны продолжать проходить.
7. Сиды: `scripts/seed.py` — заполнить БД демо-данными из JSON-файлов.

## Подсказки
* `DATABASE_URL` — единственное, что меняется между local/test/docker/prod.
* `SQLite in-memory` + `StaticPool` обязателен, иначе каждый коннект — новая БД.
* Не создавай таблицы в коде приложения (`create_all` в проде — плохо): только Alembic.
* Проверка: `alembic upgrade head` на пустой БД, затем `alembic downgrade base` — оба проходят.

## Definition of Done
- [ ] Данные читаются из БД, JSON-файлы больше не используются в рантайме
- [ ] Миграции применяются и откатываются
- [ ] Все тесты задач 01–04 зелёные на тестовой БД
- [ ] `DATABASE_URL` документирован в README, секретов в коде нет
