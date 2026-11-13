from datetime import date
import os
import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import EmailStr
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.app.core.database import get_db
from api.app.models.teachers_model import Teacher
from api.app.schemas.teacher_scheme import TeacherResponse

router = APIRouter(prefix="/api/teachers", tags=["teachers"])

UPLOAD_DIR = Path("frontend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_or_404(teacher_id: int, db: Session) -> Teacher:
  teacher = db.get(Teacher, teacher_id)
  if not teacher:
    raise HTTPException(404, "Преподаватель не найден")
  return teacher


@router.get("", response_model=List[TeacherResponse])
def get_teachers(db: Session = Depends(get_db)):
  return db.query(Teacher).all()


@router.get("/positions")
def get_teacher_positions(db: Session = Depends(get_db)):
  query = text("SELECT id, name FROM teacher_positions ORDER BY id")
  result = db.execute(query).mappings().all()
  return list(result)


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
  return get_or_404(teacher_id, db)


@router.post("", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    last_name: str = Form(...),
    first_name: str = Form(...),
    middle_name: Optional[str] = Form(None),
    email: Optional[EmailStr] = Form(None),
    phone: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    degree: int = Form(0),
    academic_title: int = Form(0),
    position_id: Optional[int] = Form(None),
    hire_date: Optional[date] = Form(None),
    dismissal_date: Optional[date] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):

  teacher = Teacher(
      last_name=last_name,
      first_name=first_name,
      middle_name=middle_name,
      email=email,
      phone=phone,
      bio=bio,
      degree=degree,
      academic_title=academic_title,
      position_id=position_id,
      hire_date=hire_date,
      dismissal_date=dismissal_date,
  )
  db.add(teacher)
  db.commit()
  db.refresh(teacher)

  if file:
    file_extension = Path(file.filename).suffix
    new_filename = f"teacher_{teacher.id}{file_extension}"
    file_path = UPLOAD_DIR / new_filename

    with open(file_path, "wb") as buffer:
      shutil.copyfileobj(file.file, buffer)

    teacher.image_url = f"/uploads/{new_filename}"
    db.commit()
    db.refresh(teacher)

  return teacher


@router.patch("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    last_name: Optional[str] = Form(None),
    first_name: Optional[str] = Form(None),
    middle_name: Optional[str] = Form(None),
    email: Optional[EmailStr] = Form(None),
    phone: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    degree: Optional[int] = Form(None),
    academic_title: Optional[int] = Form(None),
    position_id: Optional[int] = Form(None),
    hire_date: Optional[date] = Form(None),
    dismissal_date: Optional[date] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):

    teacher = get_or_404(teacher_id, db)

    update_data = {
        "last_name": last_name,
        "first_name": first_name,
        "middle_name": middle_name if middle_name else None,
        "email": email if email else None,
        "phone": phone if phone else None,
        "bio": bio if bio else None,
        "degree": degree,
        "academic_title": academic_title,
        "position_id": position_id,
        "hire_date": hire_date if hire_date else None,
        "dismissal_date": dismissal_date if dismissal_date else None,
    }

    for field, value in update_data.items():
        if value is not None:
            setattr(teacher, field, value)


    if file and file.filename:
        if teacher.image_url:
            old_file_path = Path("frontend") / teacher.image_url.lstrip("/")
            if old_file_path.exists():
                os.remove(old_file_path)

        file_extension = Path(file.filename).suffix
        new_filename = f"teacher_{teacher.id}{file_extension}"
        file_path = UPLOAD_DIR / new_filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        teacher.image_url = f"/uploads/{new_filename}"

    try:
        db.commit()
        db.refresh(teacher)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Ошибка сохранения. Возможно, такой email уже занят."
        )

    return teacher


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
  teacher = get_or_404(teacher_id, db)

  if teacher.image_url:
    file_path = Path("frontend") / teacher.image_url.lstrip("/")
    if file_path.exists():
      os.remove(file_path)

  db.delete(teacher)
  db.commit()