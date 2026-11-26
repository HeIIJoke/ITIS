from sqlalchemy import Column, Integer, String, Date, Text, SmallInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True)
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    position_id = Column(Integer, nullable=True)
    degree = Column(SmallInteger, nullable=False, default=0)
    academic_title = Column(SmallInteger, nullable=False, default=0)
    email = Column(String(255))
    phone = Column(String(30))
    bio = Column(Text)
    image_url = Column(String(500))
    hire_date = Column(Date)
    dismissal_date = Column(Date)