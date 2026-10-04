from pydantic import BaseModel, Field
from datetime import datetime

class News(BaseModel):
    id: int | None = None
    title: str = Field(..., min_length=3, max_length=150)
    content: str = Field(..., min_length=5)
    category: str = "Событие"
    date: str | None = None

    # Проверка, что заголовок не состоит из одних пробелов
    def is_valid_title(self) -> bool:
        return len(self.title.strip()) >= 3

    # Установка текущей даты
    def set_current_date(self) -> None:
        if not self.date:
            self.date = datetime.now().strftime("%d.%m.%Y")