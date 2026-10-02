"""Точка входа приложения.

FastAPI отдаёт сразу три вещи:
* API            -> /api/*             (см. api/app/api/router.py)
* документацию   -> /api/docs          (Swagger UI, собирается автоматически)
* SPA-фронтенд   -> все остальные пути (index.html + статика из frontend/)

Запуск: uvicorn api.app.main:app --reload --port 8080
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from api.app.api.router import api_router
from api.app.core.config import APP_NAME, APP_VERSION, FRONTEND_DIR
from api.app.core.static_files import StaticFileError, resolve_static_path

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url=None,
    openapi_url="/api/openapi.json",
)

app.include_router(api_router)


@app.get("/{path:path}", include_in_schema=False)
async def frontend(path: str = "") -> FileResponse:
    """Отдаёт файлы фронтенда, а неизвестные пути — на SPA-роутер."""
    # Неизвестный /api/** должен отвечать JSON-ом 404, а не отдавать index.html.
    if path == "api" or path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")

    try:
        file_path = resolve_static_path(FRONTEND_DIR, path)
    except StaticFileError:
        # Попытка выйти за пределы папки frontend (path traversal).
        raise HTTPException(status_code=403, detail="Forbidden") from None
    except FileNotFoundError:
        # Файл запрошен явно (есть расширение), но его нет -> честный 404.
        raise HTTPException(status_code=404, detail="File not found") from None

    # file_path is None -> путь похож на страницу SPA, отдаём index.html.
    return FileResponse(file_path or FRONTEND_DIR / "index.html")
