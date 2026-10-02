# Один и тот же набор команд для человека и для CI.
# Windows без make: команды в правой колонке README.md.

VENV := .venv
PY := $(VENV)/Scripts/python.exe
ifeq ($(OS),Windows_NT)
	PY := $(VENV)/Scripts/python.exe
else
	PY := $(VENV)/bin/python
endif

.PHONY: help venv install dev test lint format docker-build docker-up docker-down ci

help:            ## Показать список команд
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "};{printf "  %-14s %s\n", $$1, $$2}'

venv:            ## Создать виртуальное окружение
	python -m venv $(VENV)

install: venv    ## Поставить зависимости для разработки
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r api/requirements-dev.txt

dev:             ## Запустить дев-сервер с автоперезагрузкой
	$(PY) -m uvicorn api.app.main:app --reload --port 8080

test:            ## Тесты с покрытием
	$(PY) -m pytest --cov=api --cov-report=term-missing

lint:            ## Проверка стиля
	$(PY) -m ruff check .

format:          ## Автоисправление стиля
	$(PY) -m ruff check . --fix

docker-build:    ## Собрать образ
	docker build -t itis-web:local .

docker-up:       ## Поднять контейнер
	docker compose up --build

docker-down:     ## Остановить контейнеры
	docker compose down

ci: lint test     ## То, что делает пайплайн CI: сначала линт, потом тесты
