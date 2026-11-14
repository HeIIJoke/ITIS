from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


from api.app.routers import teachers_router
from api.app.routers import news
from api.app.paths import UPLOAD_DIR


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = (BASE_DIR / "frontend").resolve()
UPLOAD_DIR = (BASE_DIR / "uploads").resolve()
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)

app.include_router(news.router)
app.include_router(teachers_router.router)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

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