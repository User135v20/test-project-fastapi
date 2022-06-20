from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
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


def check_timetable(teacher: str, date: str, db: Session):
    md = Timetable
    return db.query(md).filter(md.teacher == teacher).filter(md.day == date).first() is not None


def create_schedule_entry(student: str, teacher: str, day: str, db):
    data = Timetable(
        student=student,
        teacher=teacher,
        day=day)
    add_into_db(data, db)
    return data


def to_book_by_token(date: str, teacher: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    student = find_user_by_token(token, db)
    if student is None:
        return 'user does not have access'
    if find_user_by_email(teacher, db) is None:
        return 'no teacher with this email was found'
    if check_timetable(teacher, date, db):
        return 'teacher is busy on this day'
    try:
        to_create = create_schedule_entry(student[0].email, teacher, date, db)
        return {
            "success": True,
            "id": to_create.id}
    except:
        return 'Failed'
