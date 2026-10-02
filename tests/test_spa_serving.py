"""Тесты раздачи SPA на уровне HTTP: index.html, fallback, корректные 404.

Эти тесты дешёвые, но ловят самые частые поломки после рефакторинга:
не тот путь до статики, сломанный catch-all, «api-404 возвращает html».
"""

from fastapi.testclient import TestClient


def test_index_html_is_served(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Кафедра" in response.text


def test_unknown_page_returns_spa_shell(client: TestClient) -> None:
    """Путь без расширения — это страница SPA, отдаём index.html."""
    response = client.get("/teachers")

    assert response.status_code == 200
    assert "id=\"app\"" in response.text


def test_missing_static_file_returns_404(client: TestClient) -> None:
    assert client.get("/css/no-such-file.css").status_code == 404


def test_unknown_api_route_returns_json_404(client: TestClient) -> None:
    response = client.get("/api/no-such-endpoint")

    assert response.status_code == 404
    assert response.json()["detail"] == "API endpoint not found"


def test_openapi_schema_is_available(client: TestClient) -> None:
    assert client.get("/api/openapi.json").status_code == 200
