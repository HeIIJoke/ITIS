from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = (BASE_DIR / "frontend").resolve()

@app.get("/api/check")
def check():
    return {"status": "ok"}


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