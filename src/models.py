from sqlalchemy import Column, Integer, String, DateTime, BIGINT
from db.database import Base


class Admin(Base):
    __tablename__ = 'admin'
    id = Column(BIGINT, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    password = Column(String)


class Student(Base):
    __tablename__ = 'student'
    id = Column(BIGINT, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    password = Column(String)


class Teacher(Base):
    __tablename__ = 'teacher'
    id = Column(BIGINT, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    password = Column(String)
    skills = Column(Integer)


class Skills(Base):
    __tablename__ = 'skills'
    id = Column(BIGINT, primary_key=True)
    teacher = Column(BIGINT)
    language = Column(Integer)


class Language(Base):
    __tablename__ = 'language'
    id = Column(BIGINT, primary_key=True)
    language = Column(String)


class Timetable(Base):
    __tablename__ = 'timetable'
    id = Column(BIGINT, primary_key=True)
    student = Column(Integer)
    teacher = Column(Integer)
    day = Column(DateTime)
