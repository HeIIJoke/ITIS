# Сайт кафедры ВТИСиТ

## Локальный запуск

Скопируйте `.env.example` в `.env` и задайте `JWT_SECRET` значением из `openssl rand -hex 32`.
Затем запустите приложение и откройте [http://localhost:8080](http://localhost:8080).

```sh
docker compose up --build -d
```

Для развёртывания под HTTPS укажите `AUTH_COOKIE_SECURE=true` и задайте публичный
адрес сайта в `AUTH_ORIGIN`, например `https://itis.example.org`.

## Роли

Зарегистрируйте аккаунт через страницу «Регистрация». Новые аккаунты получают
роль гостя. Назначьте администратором существующий аккаунт через команду:

```sh
docker compose exec app python -m api.app.manage_auth my-login
```

В разделе «Роли пользователей» администратор ищет аккаунт по логину и назначает
ему роль студента или преподавателя после проверки. Администратор также может
вернуть аккаунту роль гостя.

## Существующая база

Перед запуском новой сборки примените миграцию к существующему PostgreSQL.
Для базы из предшествующего запуска Docker Compose выполните:

```sh
docker compose up -d --wait db
docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < bd/migrations/001_auth.sql
docker compose up --build -d app
```

При создании пустой базы Compose применяет миграцию автоматически.
