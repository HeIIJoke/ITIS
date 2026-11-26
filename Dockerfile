# syntax=docker/dockerfile:1

# =============================================================================
# Stage 1: builder — here we only compile/install dependencies.
# Everything installed in this stage (gcc, headers, build cache) stays here and
# does NOT end up in the final image.
# =============================================================================
FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Build-only tools needed for native wheels (uvloop / httptools from uvicorn[standard]).
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Isolated virtualenv, easy to copy into the runtime stage in one layer.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY api/requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# =============================================================================
# Stage 2: runtime — small final image: no compilers, no apt lists, no caches.
# =============================================================================
FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Run as a non-root user.
RUN groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --create-home --home-dir /app app

# Only the ready-to-use virtualenv is copied from the builder stage.
COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

# Application code: FastAPI backend + static frontend.
COPY --chown=app:app api ./api
COPY --chown=app:app frontend ./frontend

USER app

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/api/check', timeout=3).status == 200 else 1)"

CMD ["uvicorn", "api.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
