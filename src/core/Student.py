from fastapi import Depends
from sqlalchemy.orm import Session
from core.Commons import add_into_db, check_by_name, read_from_csv, create_full_name, find_by_name, delete_by_id
from core.security import oauth2_scheme, hash_password, checking_for_access_rights
from db.database import get_db
from models import Student
from schemas import CreateUserReuest


def create_student(detail: CreateUserReuest, db_connect):
    if detail.password is None:
        password = detail.password
    else:
        password = hash_password(detail.password)
    user = Student(full_name=detail.full_name, email=detail.email, password=password)
    add_into_db(user, db_connect)
    return user


def delete_student(id_user, db_connect):
    delete_by_id(id_user, Student, db_connect)
    return {"success": "True"}


def student_list(db_connect):
    model = Student
    search_result = db_connect.query(model).all()
    return None if search_result is None else search_result


def get_students_for_admin(
    db_connect: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        checking_for_access_rights(token, "admin")
        res_list = []
        for student in student_list(db_connect):
            res_list.append(student.full_name)
        return res_list if len(res_list) > 1 else "list of students is empty"

    except Exception as err:
        return err


def add_student_from_scv_file(file_name, db_connect):
    count_added = 0
    list_result_parse = read_from_csv(file_name)
    for raw_str_student in list_result_parse:
        full_name = create_full_name(raw_str_student)
        user = CreateUserReuest(full_name=full_name)
        if not check_by_name(user.full_name, db_connect):
            create_student(user, db_connect)
            count_added += 1
    return {"success": True, "number of added student": count_added}
