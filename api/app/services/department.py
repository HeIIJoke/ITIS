"""Слой сервисов: бизнес-логика и доступ к данным.

Пока данные берутся из JSON-файла (см. API/app/data/department.json).
Задача 05 — заменить этот файл на запрос в БД, не меняя роут и схему.
Именно поэтому доступ к данным вынесен в отдельный слой.
"""

import json
from functools import lru_cache

from api.app.core.config import DATA_DIR
from api.app.schemas.department import DepartmentInfo


@lru_cache(maxsize=1)
def get_department_info() -> DepartmentInfo:
    """Читает и валидирует информацию о кафедре (кэшируется на процесс)."""
    raw = json.loads((DATA_DIR / "department.json").read_text(encoding="utf-8"))
    return DepartmentInfo.model_validate(raw)
