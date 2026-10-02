# Задача 08. Docker: образы, compose, окружения

**Ветка:** `chore/docker` · **Зависимости:** нет · **Инструменты:** Docker, Docker Compose, nginx

## Чему учимся
Собирать образы правильно (кэш слоёв, непривилегированный пользователь, healthcheck),
описывать окружение compose-файлом, добавлять БД и reverse proxy.

## Что уже есть (базовый эталон)
* `Dockerfile` — python:3.11-slim, зависимости отдельным слоем, `USER appuser`,
  `HEALTHCHECK` на `/api/health`;
* `.dockerignore`;
* `docker-compose.yml` — один сервис `web`.

```bash
docker compose up --build      # http://localhost:8000
docker compose down
```

## План работы
1. **Порядок слоёв**: убедись, что правка `frontend/` **не** переустанавливает зависимости
   (`docker build` должен быть быстрым). Покажи в PR вывод сборки.
2. **Размер образа**: `docker images` до/после. Попробуй multi-stage
   (`builder` с `gcc` → `runtime`) и сравни. Цель: < 200 MB.
3. **БД**: добавь сервис `db` (postgres:16-alpine) с `volumes: pgdata`, `healthcheck`,
   переменные из `.env` (`.env.example` в репозиторий, `.env` — в `.gitignore`).
   Приложение должно ждать готовности БД (`depends_on: condition: service_healthy`).
4. **Reverse proxy**: сервис `nginx`, отдаёт `frontend/` напрямую (быстрее) и
   проксирует `/api` на `web`. Домен, gzip, кэш статики.
5. **Профили compose**: `dev` (автоперезагрузка, код через volume) и `prod`
   (без volume, `--workers 4`). Команда: `docker compose --profile prod up -d`.
6. **Проверка healthcheck**: `docker inspect --format "{{.State.Health.Status}}" itis-web`
   должен быть `healthy`. Сломай `health`-роут — контейнер становится `unhealthy`.

## Подсказки
* `COPY requirements` до `COPY кода` — главный приём кэширования.
* Не запускай приложение от root: `USER appuser` уже есть, не убирай его.
* `docker compose logs -f web` — первое, что смотрим при падении.
* Секреты не кладём в образ: только `environment`/`env_file`.

## Definition of Done
- [ ] `docker compose up --build` поднимает сайт, `/api/health` отвечает
- [ ] Контейнер `healthy`, приложение работает не от root
- [ ] Образ < 200 MB, размер и время сборки указаны в PR
- [ ] `.env.example` описывает все переменные, `.env` не в git
- [ ] README обновлён командами compose
