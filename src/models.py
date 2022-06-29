from sqlalchemy import Column, Integer, String, DateTime, BIGINT, ForeignKey
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
    email = Column(String, nullable=True)
    password = Column(String, nullable=True)
    skills = Column(Integer)


class Timetable(Base):
    __tablename__ = 'timetable'
    id = Column(BIGINT, primary_key=True)
    student = Column(Integer, ForeignKey("student.id"))
    teacher = Column(Integer, ForeignKey("teacher.id"))
    day = Column(DateTime)


class Language(Base):
    __tablename__ = 'language'
    id = Column(BIGINT, primary_key=True)
    language = Column(String, nullable=True)


class Skills(Base):
    __tablename__ = 'skills'
    id = Column(BIGINT, primary_key=True)
    teacher = Column(BIGINT, ForeignKey("teacher.id"))
    language = Column(Integer, ForeignKey("language.id"))
