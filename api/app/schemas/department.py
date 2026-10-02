"""Pydantic-схемы: описывают контракт API (что именно отдаём клиенту).

Схема — это «договор» между бэкендом и фронтендом.
Меняешь схему — меняешь контракт, значит правишь и фронтенд, и тесты.
"""

from pydantic import BaseModel, Field


class DepartmentContacts(BaseModel):
    email: str = Field(examples=["kafedra@university.ru"])
    phone: str = Field(examples=["+7 (495) 123-45-67"])
    address: str = Field(examples=["г. Москва, ул. Университетская, 1, ауд. 301"])


class DepartmentInfo(BaseModel):
    """Краткая информация о кафедре для главной страницы."""

    short_name: str = Field(examples=["ВТИСиТ"])
    full_name: str
    faculty: str
    head: str = Field(description="ФИО заведующего кафедрой")
    founded: int = Field(description="Год основания кафедры")
    about: str
    contacts: DepartmentContacts
