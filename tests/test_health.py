"""Тесты служебного роута /api/health."""

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    # Arrange / Act
    response = client.get("/api/health")

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_reports_version_and_env(client: TestClient) -> None:
    body = client.get("/api/health").json()

    assert body["version"]  # версия должна быть заполнена
    assert body["env"] == "local"  # в тестах окружение по умолчанию local
