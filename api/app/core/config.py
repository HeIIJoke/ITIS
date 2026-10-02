"""Конфигурация приложения: пути и настройки из переменных окружения.

Правила:
* секреты и адреса НЕ хардкодим — только через переменные окружения;
* настройки читаются один раз при импорте, поведение предсказуемо;
* один файл — единственное место, где читается окружение.
"""

import os
from pathlib import Path

# --- Пути -----------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[3]  # корень репозитория
FRONTEND_DIR = BASE_DIR / "frontend"  # статика SPA (html/css/js)
DATA_DIR = BASE_DIR / "api" / "app" / "data"  # json-заглушки вместо БД

# --- Настройки ------------------------------------------------------------
APP_NAME = os.getenv("APP_NAME", "Сайт кафедры ВТИСиТ")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")  # local | docker | ci | prod
