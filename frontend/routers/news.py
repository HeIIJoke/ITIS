import shutil
import uuid

from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from api.app.core.database import get_db
from api.app.models.news import News, NewsCategory
#from api.app.schemas.news import NewsCreate

router = APIRouter(
    prefix="/api/news",
    tags=["Новости"]
)

UPLOAD_DIR = Path("uploads/news")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

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

# Получение новости
@router.get("/{news_id}")
def get_news_by_id(news_id: int, db: Session = Depends(get_db)):
    news = (
        db.query(News, NewsCategory.name)
        .outerjoin(
            NewsCategory,
            News.category_id == NewsCategory.id
        )
        .filter(News.id == news_id)
        .first()
    )

    if news is None:
        raise HTTPException(
            status_code=404,
            detail="Новость не найдена"
        )

    item, category = news

    return {
        "id": item.id,
        "title": item.title,
        "content": item.content,
        "category": category,
        "category_id": item.category_id,
        "publish_date": item.publish_date,
        "image_url": item.image_url,
        "is_event": item.is_event or False
    }

# Публикация новости
@router.post("", status_code=201)
def create_news(
    title: str = Form(..., min_length=5, max_length=150),
    content: str = Form(..., min_length=10),
    category_id: int = Form(...),
    is_event: bool = Form(False),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    image_path = None

    try:
        # Проверяем категорию
        category = (
            db.query(NewsCategory)
            .filter(NewsCategory.id == category_id)
            .first()
        )

        if category is None:
            raise HTTPException(
                status_code=400,
                detail="Выбранная категория не существует"
            )

        # Проверяем загруженное изображение
        if image and image.filename:
            allowed_types = [
                "image/jpeg",
                "image/png",
                "image/webp"
            ]

            if image.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail="Разрешены только JPG, PNG и WEBP"
                )

            # Проверяем размер файла (5 МБ)
            image.file.seek(0, 2)
            file_size = image.file.tell()
            image.file.seek(0)

            if file_size > 5 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail="Размер изображения не должен превышать 5 МБ"
                )

            extension = Path(image.filename).suffix.lower()

            if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
                raise HTTPException(
                    status_code=400,
                    detail="Недопустимый формат файла"
                )

            # Создаём уникальное имя файла
            filename = f"{uuid.uuid4().hex}{extension}"

            image_path = UPLOAD_DIR / filename

            # Сохраняем изображение
            with image_path.open("wb") as file:
                shutil.copyfileobj(image.file, file)

            # Путь, который будет храниться в БД
            image_url = f"/uploads/news/{filename}"
        else:
            image_url = None

        # Создаём новость
        new_news = News(
            category_id=category.id,
            title=title.strip(),
            content=content.strip(),
            image_url=image_url,
            is_event=is_event
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

        # Удаляем файл, если новость не сохранилась
        if image_path and image_path.exists():
            image_path.unlink()

        print(f"Ошибка публикации новости: {error}")

        raise HTTPException(
            status_code=500,
            detail="Не удалось опубликовать новость"
        )