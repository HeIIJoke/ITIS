
from datetime import date
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class Degree(IntEnum):
    NONE      = 0
    CANDIDATE = 1
    DOCTOR    = 2


class AcademicTitle(IntEnum):
    NONE      = 0
    DOCENT    = 1
    PROFESSOR = 2


class TeacherBase(BaseModel):
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    position_id: Optional[int] = None
    degree: Degree = Degree.NONE
    academic_title: AcademicTitle = AcademicTitle.NONE
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None
    hire_date: Optional[date] = None
    dismissal_date: Optional[date] = None


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    position_id: Optional[int] = None
    degree: Optional[Degree] = None
    academic_title: Optional[AcademicTitle] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    image_url: Optional[str] = None
    hire_date: Optional[date] = None
    dismissal_date: Optional[date] = None


class TeacherResponse(TeacherBase):
    id: int
    model_config = ConfigDict(from_attributes=True)