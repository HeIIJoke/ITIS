from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from api.app.core.database import Base


class NewsCategory(Base):
    __tablename__ = "news_categories"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

class News(Base):
    __tablename__ = "news"
    __table_args__ = {"schema": "public"}
    id = Column(Integer, primary_key=True, index=True)

    category_id = Column(
        Integer,
        ForeignKey("public.news_categories.id")
    )

    # author_id = Column(Integer, ForeignKey("public.users.id"))
    title = Column(String(150), nullable=False)
    content = Column(Text, nullable=False)
    publish_date = Column(DateTime, server_default=func.current_timestamp())
    image_url = Column(String(255))
    is_event = Column(Boolean, default=False)