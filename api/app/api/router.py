"""Сборка всех API-роутов в один роутер с префиксом /api.

Здесь только «монтаж»: импорт роутов и подключение. Бизнес-логики тут нет.
Чтобы добавить свою фичу — допишите одну строку include_router().
"""

from fastapi import APIRouter

from api.app.api.routes import department, health

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(department.router)


@api_router.get("/check", tags=["service"], summary="Проверка связи (устаревший)")
def check() -> dict[str, str]:
    """Оставлен для совместимости: использовался в первой версии сайта."""
    return {"status": "ok"}
