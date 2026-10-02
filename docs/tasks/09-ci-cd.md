# Задача 09. CI/CD: полная цепочка на GitHub Actions

**Ветка:** `chore/ci` · **Зависимости:** 08 (docker) · **Инструменты:** GitHub Actions, ghcr.io, кэш

## Чему учимся
Автоматизировать всё, что делается руками: линт, тесты, сборку, публикацию образа,
деплой. Плюс защита веток и секреты.

## Что уже есть (базовый эталон)
`.github/workflows/ci.yml` — три этапа: `lint` → `test` (matrix) → `docker` + smoke-тест.
Правило: следующий этап только после успеха предыдущего (`needs`).

## План работы
1. **Кэш и скорость**: замерь время пайплайна. Включи кэш `pip` (уже есть) и кэш
   Docker Buildx (`actions/cache` или `docker/build-push-action` с `cache-from/to: type=gha`).
   Цель: пайплайн < 3 минут.
2. **Матрица**: добавь ОС (`ubuntu-latest`, `windows-latest`) — убедись, что тесты
   не зависят от ОС и разделителей пути.
3. **Артефакты**: сохраняй отчёт покрытия (`actions/upload-artifact`) и HTML-отчёт
   тестов; на падении — логи контейнера.
4. **CD (продолжение пайплайна)**: новый workflow `release.yml`
   * триггер: тег `v*.*.*` или push в `main`;
   * сборка образа и публикация в **ghcr.io** с тегами `latest`, `sha-<short>`, `v1.2.3`;
   * `permissions: packages: write`, вход через `GITHUB_TOKEN`;
   * деплой: job с `environment: production`, `needs: build`, шаги по SSH
     (`appleboy/ssh-action`) или `docker compose pull && up -d` на сервере.
   * после деплоя — **smoke-тест на прод** (`curl /api/health`), иначе откат.
5. **Секреты**: `SSH_HOST`, `SSH_USER`, `SSH_KEY`, `DATABASE_URL` — через
   GitHub Secrets/Environments, в коде их нет. Проверь, что нет утечки в логах.
6. **Защита**: включи branch protection для `main` и `develop`:
   обязательные проверки `lint`, `test`; запрет force-push; требование 1 approve.
7. **Бонус**: бейдж статуса в README, `concurrency` (отмена устаревших запусков),
   `paths-ignore` для `*.md`.

## Подсказки
* Отладка workflow — только через лог: `actions/checkout@v4` + шаг `env` печатает контекст.
* `needs` без `if: always()` не запустит job после падения предыдущего.
* Тег образа = git-тег = версия. Это делает деплой и откат предсказуемыми.
* Пайплайн должен быть одинаковым для PR и для релиза — иначе CI врёт.

## Definition of Done
- [ ] `lint` → `test` → `docker` зелёные на PR и на push в `develop`
- [ ] По тегу собирается и публикуется образ в ghcr.io
- [ ] Деплой + smoke-тест на окружении `production`, есть план отката
- [ ] Branch protection настроен, скриншот в PR
- [ ] README содержит бейдж и описание пайплайна
