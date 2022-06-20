from datetime import datetime
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import EmailStr
from sqlalchemy.orm import Session
from core.logic import find_user_by_email, add_into_db
from core.security import SECRET_KEY, ALGORITHM
from db.database import get_db
from models import Timetable

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def find_user_by_token(token: str, db: Session):
    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    role = payload.get("role")
    email = payload.get("email")
    return find_user_by_email(email, db, role)


def check_timetable_for_teacher(user: str, db: Session, from_date: str, to_date: str = None):
    md = Timetable
    if to_date is None:
        to_date = from_date
    return db.query(md).filter(md.teacher == user, md.day >= from_date, md.day <= to_date).first() is not None


def check_timetable_for_student(user: str, db: Session, from_date: str, to_date: str = None):
    md = Timetable
    if to_date is None:
        to_date = from_date
    return db.query(md).filter(md.student == user, md.day >= from_date, md.day <= to_date).order_by(md.day.asc()).all()


def create_schedule_entry(student: str, teacher: str, day: str, db):
    data = Timetable(
        student=student,
        teacher=teacher,
        day=datetime.strptime(day, '%Y-%m-%d'))
    add_into_db(data, db)
    return data


def to_book_by_token(date, teacher: EmailStr, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    student = find_user_by_token(token, db)
    if student is None:
        return 'user does not have access'
    if find_user_by_email(teacher, db) is None:
        return 'no teacher with this email was found'
    if check_timetable_for_teacher(teacher, db, date):
        return 'teacher is busy on this day'
    try:
        to_create = create_schedule_entry(student[0].email, teacher, date, db)
        return {
            "success": True,
            "id": to_create.id}
    except:
        return 'Failed attempt to add an entry to the schedule'


def list_of_classes_for_a_student(from_date, to_date, db: Session = Depends(get_db),
                                  token: str = Depends(oauth2_scheme)):
    student = find_user_by_token(token, db)
    timetable = check_timetable_for_student(student.email, db, from_date, to_date)
    if len(timetable) < 1:
        return 'these dates are free'
    timetable_res_list = list()
    for el in timetable:
        teacher = find_user_by_email(el.teacher, db, 'teacher').full_name
        timetable_res_list.append(str(el.day) + "  " + str(teacher))
    return timetable_res_list
