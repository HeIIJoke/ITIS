"""Эталонная фича «Информация о кафедре» — шаблон для всех остальных.

Как добавить свою фичу (ровно 4 шага):
1. схема данных -> api/app/schemas/<фича>.py
2. логика      -> api/app/services/<фича>.py
3. роут        -> api/app/api/routes/<фича>.py и строчка в api/app/api/router.py
4. тест        -> tests/test_<фича>.py

Роут не содержит логики: только принимает запрос и зовёт сервис.
"""

from fastapi import APIRouter

from api.app.schemas.department import DepartmentInfo
from api.app.services.department import get_department_info

router = APIRouter(prefix="/department", tags=["department"])


@router.get("", response_model=DepartmentInfo, summary="Информация о кафедре")
def read_department() -> DepartmentInfo:
    """Краткая информация о кафедре для главной страницы."""
    return get_department_info()
