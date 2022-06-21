from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session
from core.security import hash_password, ALGORITHM, SECRET_KEY
from db.database import Base
from models import Student, Teacher, Admin, Language, Timetable
from schemas import CreateUserReuest

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def add_into_db(data: Base, db: Session):
    db.add(data)
    db.commit()


def delete_in_db(data, db: Session):
    db.delete(data)
    db.commit()


def create_admin(detail: CreateUserReuest, db: Session):
    user = Admin(
        full_name=detail.full_name,
        email=detail.email,
        password=hash_password(detail.password)
    )
    add_into_db(user, db)
    return user


def create_student(detail: CreateUserReuest, db: Session):
    user = Student(
        full_name=detail.full_name,
        email=detail.email,
        password=hash_password(detail.password)
    )
    add_into_db(user, db)
    return user


def get_language(db: Session, id_language):
    return db.query(Language).filter(Language.id == id_language).first().language


def get_language_id(language: str, db: Session):
    search_result = db.query(Language).filter(Language.language == language).first()
    if search_result is None:
        db.add(Language(language=language))
        db.commit()
        search_result = db.query(Language).filter(Language.language == language).first()
    return search_result.id


def create_teacher(detail: CreateUserReuest, db: Session):
    user = Teacher(
        full_name=detail.full_name,
        email=detail.email,
        password=hash_password(detail.password),
        language=get_language_id(detail.language, db)
    )
    add_into_db(user, db)
    return user


def create_schedule_entry(student: str, teacher: str, day: str, db):
    data = Timetable(
        student=student,
        teacher=teacher,
        day=datetime.strptime(day, '%Y-%m-%d'))
    add_into_db(data, db)
    return data


DICT_ROLE_MODEL_FUNC = \
    {"admin": ["admin", Admin, create_admin],
     "student": ["student", Student, create_student],
     "teacher": ["teacher", Teacher, create_teacher]
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
        id_language = get_language_id(language, db)
        search_result = db.query(model).filter(model.language == id_language).all()
    return None if search_result is None else search_result


def find_user_by_token(token: str, role, db: Session):
    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    try:
        checking_for_access_rights(token, role)
        token_role = payload.get("role")
        email = payload.get("email")
        return find_user_by_email(email, db, token_role)
    except:
        raise Exception('invalid token')


def checking_for_access_rights(token, role):
    if role != jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM).get("role"):
        raise Exception('no access rights')


def check_to_date_param(from_date, to_date):
    if to_date is not None and datetime.strptime(to_date, '%Y-%m-%d') < datetime.strptime(from_date, '%Y-%m-%d'):
        raise Exception('invalid to_date parameter')
    return from_date if to_date is None else to_date


DICT_STUDENT_TEACHER = \
    {
        "student": Timetable.student,
        "teacher": Timetable.teacher
    }


def check_timetable(user, role, db: Session, from_date, to_date):
    md = Timetable
    to_date = check_to_date_param(from_date, to_date)
    return db.query(md).filter(DICT_STUDENT_TEACHER.get(role) == user, md.day >= from_date, md.day <= to_date).order_by(
        md.day.asc()).all()


def get_timetable(token, db, role, from_date, to_date):
    checking_for_access_rights(token, role)
    user = find_user_by_token(token, role, db)
    timetable = check_timetable(user.email, role, db, from_date, to_date)
    return timetable
