# Сайт кафедры ВТИСиТ — учебная заготовка «идеального проекта»

Репозиторий-тренажёр: **эталонная структура сайта кафедры** + набор задач, каждая
из которых прокачивает отдельный инструмент (Git, тесты, Docker, CI/CD, БД, auth).

Правило проекта: **любая работа начинается с фичи и теста к ней.** Образец уже
реализован — фича «Информация о кафедре» (`GET /api/department`) и её тесты.

---

## Быстрый старт

```bash
git clone https://github.com/HeIIJoke/ITIS.git && cd ITIS
make install          # venv + зависимости для разработки
make dev              # сайт: http://localhost:8080  API-доки: /api/docs
make test             # тесты
make lint             # стиль кода
```

Windows без `make`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r api\requirements-dev.txt
python -m uvicorn api.app.main:app --reload --port 8080
python -m pytest
```

Docker:

```bash
docker compose up --build   # http://localhost:8000
```

---

## Стек

Python 3.11 · FastAPI · Pydantic · Uvicorn · pytest · ruff · Docker · GitHub Actions
Фронтенд — ванильный HTML/CSS/JS (SPA-роутер), без сборки.

## Структура

```
api/                     бэкенд (FastAPI)
  app/
    main.py              точка входа: API + Swagger + раздача SPA
    core/config.py       пути и настройки из переменных окружения
    core/static_files.py поиск файла статики + защита от path traversal
    api/router.py        сборка роутов с префиксом /api
    api/routes/          роуты по фичам (1 файл = 1 фича)
    schemas/             Pydantic-схемы = контракт API
    services/            логика и доступ к данным
    data/                json-заглушки вместо БД
  requirements.txt       зависимости для прода
  requirements-dev.txt   зависимости для разработки и CI
frontend/                фронтенд (SPA)
  index.html             каркас: шапка, меню, <main id="app">, подвал
  pages/                 разметка страниц
  js/main.js             общая логика: apiGet()
  js/router.js           роутер SPA
  js/pages/              логика страниц: init<Страница>()
  css/base.css           переменные и каркас
  css/components/        переиспользуемые стили (карточки, формы)
  css/pages/             стили страниц
tests/                   тесты pytest (зеркало фич)
  conftest.py            фикстура client (TestClient, без сети и портов)
  test_health.py         /api/health
  test_department.py     эталонная фича «кафедра»
  test_spa_serving.py    HTTP-уровень: index.html, SPA-fallback, 404
  test_static_files.py   unit-тесты раздачи статики (без FastAPI)
  test_frontend_wiring.py пути, страницы и обработчики SPA
docs/
  ARCHITECTURE.md        почему так устроено, куда класть код
  CONVENTIONS.md         git-flow, коммиты, ревью, определение готовности
  tasks/                 задания участникам
.github/workflows/ci.yml lint -> test -> docker (smoke)
Dockerfile / docker-compose.yml
Makefile                 все команды в одном месте
```

## API

| Метод | Путь | Назначение |
|---|---|---|
| GET | `/api/health` | статус сервиса (Docker/CI/мониторинг) |
| GET | `/api/department` | информация о кафедре (эталонная фича) |
| GET | `/api/docs` | Swagger UI |
| GET | `/api/check` | устаревшая проверка связи |

## Как добавить свою фичу (5 шагов)

1. `api/app/schemas/<фича>.py` — схема данных (контракт).
2. `api/app/services/<фича>.py` — логика и доступ к данным.
3. `api/app/api/routes/<фича>.py` + строчка в `api/app/api/router.py` — роут.
4. `tests/test_<фича>.py` — тесты (сначала падающие, потом код).
5. `frontend/pages/<страница>.html`, `frontend/js/pages/<страница>.js`,
   роут в `frontend/js/router.js`, стили в `frontend/css/pages/`.

Эталон для копирования — задача 00 и файлы фичи `department`.

## Задачи участников

Один участник — одна задача. Ветка и порядок работы описаны в `docs/CONVENTIONS.md`.

| # | Задача | Инструменты | Файл |
|---|---|---|---|
| 00 | Стартовая фича + тест (эталон, готово) | FastAPI, pytest | [docs/tasks/00-kickstart.md](docs/tasks/00-kickstart.md) |
| 01 | Преподаватели: каталог и профиль | REST, фильтры, JS | [01-teachers](docs/tasks/01-teachers.md) |
| 02 | Расписание | валидация, Enum, тесты | [02-schedule](docs/tasks/02-schedule.md) |
| 03 | Новости кафедры (CRUD) | REST, коды ответов | [03-news](docs/tasks/03-news.md) |
| 04 | Наука и публикации | связи, агрегаты | [04-science](docs/tasks/04-science.md) |
| 05 | Интеграция с БД + миграции | SQLAlchemy, Alembic | [05-database](docs/tasks/05-database.md) |
| 06 | Аутентификация и админка | JWT, роли, Depends | [06-auth](docs/tasks/06-auth.md) |
| 07 | Тестирование и покрытие | pytest, Playwright | [07-testing](docs/tasks/07-testing.md) |
| 08 | Docker и окружения | Docker, Compose, nginx | [08-docker](docs/tasks/08-docker.md) |
| 09 | CI/CD и деплой | GitHub Actions, ghcr | [09-ci-cd](docs/tasks/09-ci-cd.md) |
| 10 | Git-практикум | ветки, PR, конфликты | [10-git](docs/tasks/10-git.md) |

Рекомендуемый порядок: **00 → (01…04) → 05 → 06 → 07 → 08 → 09 → 10**.
Задачи 01–04 можно делать параллельно, они не пересекаются по файлам.

## Definition of Done (кратко)

Задача закрыта, когда: есть тесты (и они падают при поломке фичи), `make lint`
и `make test` зелёные, CI на PR зелёный, есть approve, документация обновлена.

Подробно: [docs/CONVENTIONS.md](docs/CONVENTIONS.md) · Архитектура: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
