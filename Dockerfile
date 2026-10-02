# --- Эталонный образ для сайта кафедры ------------------------------------
# 1) зависимости отдельным слоем  -> быстрый ребилд
# 2) непривилегированный пользователь -> безопасность
# 3) HEALTHCHECK на /api/health    -> самовосстановление в оркестраторе

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=docker

WORKDIR /app

COPY api/requirements.txt api/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r api/requirements.txt

COPY api ./api
COPY frontend ./frontend

RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys,urllib.request; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health').status == 200 else 1)"

CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
