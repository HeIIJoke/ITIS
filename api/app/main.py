from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles


from api.app.core.auth import signing_key
from api.app.routers import auth, news, teachers_router
from api.app.paths import UPLOAD_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    signing_key()
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def set_response_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith(("/api/auth/", "/api/admin/users")):
        response.headers["Cache-Control"] = "no-store"
    elif request.url.path.startswith("/uploads/"):
        response.headers["Content-Security-Policy"] = "sandbox"
        response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, error: RequestValidationError):
    if request.url.path.rstrip("/") in ("/api/auth/register", "/api/auth/login"):
        details = [
            {key: item[key] for key in ("loc", "msg", "type")} for item in error.errors()
        ]
        return JSONResponse({"detail": details}, status_code=422)
    return await request_validation_exception_handler(request, error)

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = (BASE_DIR / "frontend").resolve()


app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)

app.include_router(auth.router)
app.include_router(auth.admin_router)
app.include_router(news.router)
app.include_router(teachers_router.router)

@app.get("/api/check")
def check():
    return {"status": "ok"}

@app.get("/assets/{path:path}", include_in_schema=False)
async def assets(path: str):
    file_path = (FRONTEND_DIR / path).resolve()

    if not file_path.is_relative_to(FRONTEND_DIR):
        raise HTTPException(status_code=403, detail="Forbidden")

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)


@app.get("/{path:path}", include_in_schema=False)
async def frontend(path: str = ""):
    if not path:
        return FileResponse(FRONTEND_DIR / "index.html")

    file_path = (FRONTEND_DIR / path).resolve()

    if not file_path.is_relative_to(FRONTEND_DIR):
        raise HTTPException(status_code=403, detail="Forbidden")

    if file_path.is_file():
        return FileResponse(file_path)

    if Path(path).suffix:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(FRONTEND_DIR / "index.html")
