@echo off
REM Запуск дев-сервера на Windows без make.
REM Нужен активированный .venv с установленными зависимостями (см. README).
python -m uvicorn api.app.main:app --reload --port 8080
