from sqlalchemy.orm import Session
from core.security import hash_password
from db.database import Base
from models import Student, Teacher, Admin, Language
from schemas import CreateUserReuest


def add_into_db(data: Base, db: Session):
    db.add(data)
    db.commit()


def delete_in_db(data, db: Session):
    db.delete(data)
    db.commit()


def create_admin_data(detail: CreateUserReuest, db: Session):
    user = Admin(
        full_name=detail.full_name,
        email=detail.email,
        password=hash_password(detail.password)
    )
    add_into_db(user, db)
    return user


def create_student_data(detail: CreateUserReuest, db: Session):
    user = Student(
        full_name=detail.full_name,
        email=detail.email,
        password=hash_password(detail.password)
    )
    add_into_db(user, db)
    return user


def id_from_the_language_table(language: str, db: Session):
    search_result = db.query(Language).filter(Language.language == language).first()
    if search_result is None:
        db.add(Language(language=language))
        db.commit()
        search_result = db.query(Language).filter(Language.language == language).first()
    return search_result.id


def create_teacher_data(detail: CreateUserReuest, db: Session):
    user = Teacher(
        full_name=detail.full_name,
        email=detail.email,
        password=hash_password(detail.password),
        language=id_from_the_language_table(detail.language, db)
    )
    add_into_db(user, db)
    return user


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
        to_create = DICT_ROLE_MODEL_FUNC.get(user_role)[2](detail, db)
        return {
            "success": True,
            "id": to_create.id}
    except:
        return 'Failed to signup user'


def search(mail: str, md: Base, db: Session):
    return db.query(md).filter(md.email == mail).first()


def find_user_and_role_by_email(email: str, db: Session):
    for value in DICT_ROLE_MODEL_FUNC.values():
        model = value[1]
        search_result = search(email, model, db)
        if search_result is not None:
            return [search_result, value[0]]
    return None


def find_user_by_email(email: str, db: Session, role=None):
    if role is None:
        for value in DICT_ROLE_MODEL_FUNC.values():
            model = value[1]
            search_result = search(email, model, db)
            if search_result is not None:
                return search_result
    else:
        model = DICT_ROLE_MODEL_FUNC[role][1]
        search_result = search(email, model, db)
    return None if search_result is None else search_result


def teachers_list(db: Session, language=None):
    model = Teacher
    if language is None:
        search_result = db.query(model).filter(model.language is not None).all()
    else:
        id_language= id_from_the_language_table(language, db)
        search_result = db.query(model).filter(model.language == id_language).all()
    return None if search_result is None else search_result


def get_language(db: Session, id_language):
    return db.query(Language).filter(Language.id == id_language).first().language
