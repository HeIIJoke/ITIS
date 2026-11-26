from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class NewsCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=150)
    content: str = Field(..., min_length=5)
    category_id: int
    image_url: str | None = None
    is_event: bool = False

class NewsResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str | None = None
    publish_date: datetime
    image_url: str | None = None
    is_event: bool = False

    model_config = ConfigDict(from_attributes=True)