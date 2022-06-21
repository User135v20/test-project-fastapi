from datetime import datetime
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import EmailStr
from sqlalchemy.orm import Session
from core.logic import find_user_by_email, add_into_db, delete_in_db, teachers_list, get_language
from core.security import SECRET_KEY, ALGORITHM
from db.database import get_db
from models import Timetable

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def find_user_by_token(token: str, db: Session):
    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    role = payload.get("role")
    email = payload.get("email")
    return find_user_by_email(email, db, role)

def checking_for_access_rights(token, role):
    return role == jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM).get("role")

def check_to_date_param(from_date, to_date):
    if to_date is not None and datetime.strptime(to_date, '%Y-%m-%d') < datetime.strptime(from_date, '%Y-%m-%d'):
        raise
    return from_date if to_date is None else to_date


def check_timetable_for_teacher(user, db: Session, from_date, to_date):
    md = Timetable
    to_date = check_to_date_param(from_date, to_date)
    return db.query(md).filter(md.teacher == user, md.day >= from_date, md.day <= to_date).order_by(md.day.asc()).all()


def check_timetable_for_student(user, db: Session, from_date, to_date):
    md = Timetable
    to_date = check_to_date_param(from_date, to_date)
    return db.query(md).filter(md.student == user, md.day >= from_date, md.day <= to_date).order_by(md.day.asc()).all()


def create_schedule_entry(student: str, teacher: str, day: str, db):
    data = Timetable(
        student=student,
        teacher=teacher,
        day=datetime.strptime(day, '%Y-%m-%d'))
    add_into_db(data, db)
    return data


def to_book(date, teacher: EmailStr, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    if checking_for_access_rights(token, 'student') is False:
        return 'no access rights'
    student = find_user_by_token(token, db)
    if student is None:
        return 'user does not have access'
    if find_user_by_email(teacher, db) is None:
        return 'no teacher with this email was found'
    if len(check_timetable_for_teacher(teacher, db, date)) < 1:
        return 'teacher is busy on this day'
    if len(check_timetable_for_student(student, db, date)) < 1:
        return 'student is busy on this day'
    try:
        to_create = create_schedule_entry(student[0].email, teacher, date, db)
        return {
            "success": True,
            "id": to_create.id}
    except:
        return 'Failed attempt to add an entry to the schedule'


def list_of_classes_for_a_student(from_date, to_date=None, db: Session = Depends(get_db),
                                  token: str = Depends(oauth2_scheme)):
    if checking_for_access_rights(token, 'student') is False:
        return 'no access rights'
    to_date = check_to_date_param(from_date, to_date)
    student = find_user_by_token(token, db)
    timetable = check_timetable_for_student(student.email, db, from_date, to_date)
    if len(timetable) < 1:
        return 'this date is free or these dates are free'
    timetable_res_list = list()
    for el in timetable:
        teacher = find_user_by_email(el.teacher, db, 'teacher').full_name
        timetable_res_list.append(str(el.day) + "  " + str(teacher))
    return timetable_res_list


def cancel_a_booked_lesson(date, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    if checking_for_access_rights(token, 'student') is False:
        return 'no access rights'
    student = find_user_by_token(token, db)
    timetable = check_timetable_for_student(student.email, db, date)
    if len(timetable) < 1:
        return 'this date is free'
    delete_in_db(timetable[0], db)
    return date + ' is free'


def find_free_teachers(from_date, to_date=None, language=None, db: Session = Depends(get_db),
                       token: str = Depends(oauth2_scheme)):
    if checking_for_access_rights(token, 'student') is False:
        return 'no access rights'
    if find_user_by_token(token, db) is None:
        return 'user does not exist'
    try:
        to_date = check_to_date_param(from_date, to_date)
    except Exception:
        return 'invalid to_date params'
    list_teachers = teachers_list(db, language)
    list_free_teachers = list()
    for el in list_teachers:
        lessons_for_the_specified_dates = check_timetable_for_teacher(el.email, db, from_date, to_date)
        if len(lessons_for_the_specified_dates) < 1:
            if language is None:
                teacher_language = get_language(db, el.language)
                list_free_teachers.append(el.full_name + " | " + teacher_language)
            else:
                list_free_teachers.append(el.full_name)
    return list_free_teachers
