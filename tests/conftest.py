"""Общие фикстуры для всех тестов.

Тесты ходят в приложение напрямую через TestClient — сервер поднимать не нужно.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Чтобы работал `import api...` при запуске pytest из любой папки.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from api.app.main import app  # noqa: E402  (импорт после правки sys.path)


@pytest.fixture(scope="session")
def client() -> TestClient:
    """HTTP-клиент к приложению (in-process, без сети и портов)."""
    with TestClient(app) as test_client:
        yield test_client
