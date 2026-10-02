# Задача 01. Преподаватели (каталог + профиль)

**Ветка:** `feature/teachers` · **Зависимости:** нет · **Инструменты:** FastAPI, Pydantic, pytest, JS

## Чему учимся
Проектировать REST-ресурс «список + профиль», фильтры через query-параметры,
динамические роуты SPA, рисуем карточки на клиенте.

## Контракт API
| Метод | Путь | Описание |
|---|---|---|
| GET | `/api/teachers` | список; фильтры `?q=`, `?position=`, `?degree=` |
| GET | `/api/teachers/{slug}` | профиль по slug (например `ivanov-ii`); 404 если нет |

Поля преподавателя: `slug`, `full_name`, `position`, `degree`, `email`, `phone`,
`room`, `reception_hours`, `photo_url`, `about`.

## План работы
1. **Тест-контракт** (`tests/test_teachers.py`): сначала напиши тесты на список,
   фильтр по `q`, 404 на неизвестный slug. Они падают — это нормально.
2. Схемы: `api/app/schemas/teacher.py` (`Teacher`, `TeacherShort`).
3. Сервис: `api/app/services/teachers.py` — чтение из `api/app/data/teachers.json`,
   фильтрация в Python.
4. Роуты: `api/app/api/routes/teachers.py`, подключить в `api/app/api/router.py`.
5. Фронтенд: `frontend/pages/teachers.html` + `frontend/js/pages/teachers.js`
   (в `initTeachers()` — `apiGet("/teachers")` и отрисовка карточек).
6. Добавить поля поиска/фильтра в разметку и фильтровать через query-параметры
   (фильтрация **на бэкенде**, а не в JS).
7. Профиль: роут `/teachers/:slug` в `frontend/js/router.js` — подумай,
   как роутер с параметром превратить в общий механизм (сейчас он по словарю).

## Подсказки
* `@router.get("/{slug}")` подключай **после** `@router.get("")`, иначе порядок важен не будет.
* Фильтр `q` — регистронезависимый поиск по ФИО: `full_name.lower().startswith(...)`.
* Данные держи в JSON ровно как в схеме, чтобы `model_validate` не падал.

## Definition of Done
- [ ] Тесты: список, фильтры, профиль, 404 (зелёные)
- [ ] Страница `/teachers` рендерит данные из API, фильтры работают
- [ ] `make lint && make test` зелёные, PR замержен в `develop`
