from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, index=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_teacher = Column(Boolean(), default=True)