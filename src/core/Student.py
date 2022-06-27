from fastapi import Depends
from sqlalchemy.orm import Session
from core.Commons import add_into_db, check_by_name, find_user_by_token, read_from_csv, create_full_name
from core.security import oauth2_scheme, hash_password
from db.database import get_db
from models import Student
from schemas import CreateUserReuest


def create_student(detail: CreateUserReuest, db: Session):
    if detail.password is None:
        password = detail.password
    else:
        password = hash_password(detail.password)
    user = Student(
        full_name=detail.full_name,
        email=detail.email,
        password=password
    )
    add_into_db(user, db)
    return user


def student_list(db: Session):
    model = Student
    search_result = db.query(model).all()
    return None if search_result is None else search_result

def get_list_students(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        find_user_by_token(token, 'admin', db)
        res_list = list()
        for el in student_list(db):
            res_list.append(el.full_name)
        return res_list if len(res_list) > 1 else "list of students is empty"

    except Exception as err:
        return err.args

def add_student_from_scv_file(file_name, db):
    count_added = 0
    list_result_parse = read_from_csv(file_name)
    for el in list_result_parse:
        full_name = create_full_name(el)
        user = CreateUserReuest(
            full_name=full_name)
        if not check_by_name(user.full_name, db):
            create_student(user, db)
            count_added += 1
    return {"success": True,
            "number of added student": count_added}
