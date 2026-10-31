from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from api.app.core.database import get_db
from api.app.models.news import News, NewsCategory
from api.app.schemas.news import NewsCreate

router = APIRouter(
    prefix="/api/news",
    tags=["Новости"]
)

# Получение всех новостей
@router.get("")
def get_news(db: Session = Depends(get_db)):
    try:
        news_list = (
            db.query(News, NewsCategory.name)
            .outerjoin(
                NewsCategory,
                News.category_id == NewsCategory.id
            )
            .order_by(
                News.publish_date.desc(),
                News.id.desc()
            )
            .all()
        )

        result = []

        for news, category in news_list:
            result.append({
                "id": news.id,
                "title": news.title,
                "content": news.content,
                "category": category,
                "category_id": news.category_id,
                "publish_date": news.publish_date,
                "image_url": news.image_url,
                "is_event": news.is_event or False
            })

        return result

    except Exception as error:
        print(f"Ошибка получения новостей: {error}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось загрузить новости"
        )

# Получение предустановленных категорий
@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    try:
        categories = (
            db.query(NewsCategory)
            .order_by(NewsCategory.id)
            .all()
        )

        return [
            {
                "id": category.id,
                "name": category.name
            }
            for category in categories
        ]

    except Exception as error:
        print(f"Ошибка получения категорий: {error}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось загрузить категории"
        )

# Публикация новости
@router.post("", status_code=201)
def create_news(
    news_data: NewsCreate,
    db: Session = Depends(get_db)
):
    try:
        # Проверяем, существует ли выбранная категория
        category = (
            db.query(NewsCategory)
            .filter(NewsCategory.id == news_data.category_id)
            .first()
        )

        if category is None:
            raise HTTPException(
                status_code=400,
                detail="Выбранная категория не существует"
            )

        # Создаём новость
        new_news = News(
            category_id=category.id,
            title=news_data.title.strip(),
            content=news_data.content.strip(),
            image_url=news_data.image_url,
            is_event=news_data.is_event
        )

        db.add(new_news)
        db.commit()
        db.refresh(new_news)

        return {
            "id": new_news.id,
            "title": new_news.title,
            "content": new_news.content,
            "category_id": category.id,
            "category": category.name,
            "publish_date": new_news.publish_date,
            "image_url": new_news.image_url,
            "is_event": new_news.is_event or False
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as error:
        db.rollback()
        print(f"Ошибка публикации новости: {error}")
        raise HTTPException(
            status_code=500,
            detail="Не удалось опубликовать новость"
        )