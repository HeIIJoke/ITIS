"""Тесты эталонной фичи «Информация о кафедре» (GET /api/department).

Это образец: тесты пишем вместе с фичей, а не после неё.
Структура теста — AAA: Arrange (подготовка) / Act (действие) / Assert (проверка).
"""

from fastapi.testclient import TestClient


def test_department_returns_full_contract(client: TestClient) -> None:
    response = client.get("/api/department")

    assert response.status_code == 200
    body = response.json()

    # Проверяем контракт целиком, а не только один счастливый кейс.
    assert set(body) == {
        "short_name",
        "full_name",
        "faculty",
        "head",
        "founded",
        "about",
        "contacts",
    }
    assert body["short_name"] == "ВТИСиТ"
    assert "кафедра" in body["full_name"].lower()


def test_department_contacts_are_valid(client: TestClient) -> None:
    contacts = client.get("/api/department").json()["contacts"]

    assert "@" in contacts["email"]
    assert any(ch.isdigit() for ch in contacts["phone"])
    assert contacts["address"]


def test_department_founded_is_realistic_year(client: TestClient) -> None:
    founded = client.get("/api/department").json()["founded"]

    assert 1900 < founded < 2100
