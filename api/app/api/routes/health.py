"""Служебный роут /api/health — «жив ли сервис».

Нужен инфраструктуре, а не пользователю:
* Docker HEALTHCHECK;
* smoke-тест в CI после сборки образа;
* мониторинг/балансировщик.
"""

from fastapi import APIRouter

from api.app.core.config import APP_NAME, APP_VERSION, ENVIRONMENT

router = APIRouter(tags=["service"])


@router.get("/health", summary="Статус сервиса")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "name": APP_NAME,
        "version": APP_VERSION,
        "env": ENVIRONMENT,
    }
