from sqlalchemy import Boolean, Column, Integer, String
from db.database import Base


class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)


class Student(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

class Teacher(Base):
    __tablename__ = 'teacher'
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    language = Column(String, nullable=True)


class Language(Base):
    __tablename__ = 'language'
    id = Column(Integer, primary_key=True)
    language = Column(String, nullable=False)

class Timetable(Base):
    __tablename__ = 'timetable'
    id = Column(Integer, primary_key=True)
    student = Column(String, nullable=False)
    teacher = Column(String, nullable=False)
    day = Column(String, nullable=False)
