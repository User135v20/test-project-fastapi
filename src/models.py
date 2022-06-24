from sqlalchemy import Column, Integer, String, DateTime
from db.database import Base


class Admin(Base):
    __tablename__ = 'admin'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    password = Column(String)


class Student(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    password = Column(String)

class Teacher(Base):
    __tablename__ = 'teacher'
    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    email = Column(String)
    password = Column(String)
    language = Column(Integer)


class Language(Base):
    __tablename__ = 'language'
    id = Column(Integer, primary_key=True)
    language = Column(String)

class Timetable(Base):
    __tablename__ = 'timetable'
    id = Column(Integer, primary_key=True)
    student = Column(Integer)
    teacher = Column(Integer)
    day = Column(DateTime)
