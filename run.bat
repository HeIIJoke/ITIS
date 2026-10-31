@echo off
echo Starting FastAPI server...
uvicorn api.app.main:app --reload --port 8080
pause

