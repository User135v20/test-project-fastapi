from sqlalchemy.orm import Session

from core.security import hash_password
from models import Student, Teacher, Admin
from schemas import CreateUserReuest


def create_admin_data(detail: CreateUserReuest):
    return Admin(
        full_name=detail.full_name,
        email=detail.email,
        password=hash_password(detail.password)
    )


def create_student_data(detail: CreateUserReuest):
    return Student(
        full_name=detail.full_name,
        email=detail.email,
        password=hash_password(detail.password)
    )


def create_teacher_data(detail: CreateUserReuest):
    return Teacher(
        full_name=detail.full_name,
        email=detail.email,
        password=hash_password(detail.password),
        language=detail.language
    )


DICT_ROLE_MODEL_FUNC = \
    {"admin": ["admin", Admin, create_admin_data],
     "student": ["student", Student, create_student_data],
     "teacher": ["teacher", Teacher, create_teacher_data]
     }


def add_users(detail: CreateUserReuest, db: Session):
    user_email = detail.email
    user_role = detail.role

    if find_user_by_email(user_email, db) is not None:
        return 'user with this email already exists'
    try:
        to_create = DICT_ROLE_MODEL_FUNC.get(user_role)[2](detail)
        db.add(to_create)
        db.commit()
        return {
            "success": True,
            "id": to_create.id}
    except:
        return 'Failed to signup user'


def find_user_by_email(email: str, db: Session):
    for value in DICT_ROLE_MODEL_FUNC.values():
        model = value[1]
        search_result = db.query(model).filter(model.email == email).first()
        if search_result is not None:
            return [search_result, value[0]]
    return None
