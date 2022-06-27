import csv
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy import exists
from sqlalchemy.orm import Session
from core.security import hash_password, ALGORITHM, SECRET_KEY
from db.database import Base
from models import Student, Teacher, Admin, Language, Timetable, Skills
from schemas import CreateUserReuest, UserFromCsv

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def add_into_db(data: Base, db: Session):
    db.add(data)
    db.commit()


def delete_by_id(id, model, db):
    db.query(model).filter_by(id=id).delete(synchronize_session=False)
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


def get_language_id(language, db: Session):
    search_result = db.query(Language).filter(Language.language == language).first()
    return None if search_result is None else search_result.id


def add_skill(db, teacher_id, language_id):
    data = Skills(
        teacher=teacher_id,
        language=language_id
    )
    add_into_db(data, db)
    return data.id


def add_language_to_db(language, db):
    data = Language(language=language)
    add_into_db(data, db)
    return data.id


def create_teacher(detail: CreateUserReuest, db: Session):
    if detail.password is None:
        password = detail.password
    else:
        password = hash_password(detail.password)
    user = Teacher(
        full_name=detail.full_name,
        email=detail.email,
        password=password
    )
    add_into_db(user, db)
    language_id = get_language_id(detail.language, db)
    if language_id is None:
        language_id = add_language_to_db(detail.language, db)
    user.skills = add_skill(db, user.id, language_id)
    db.commit()
    return user


def create_schedule_entry(student, teacher, day, db):
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
    user_name = detail.full_name
    user_role = detail.role

    if check_user_by_name_and_email(user_name, user_email, db):
        return 'user with this email or name already exists'
    try:
        to_create = DICT_ROLE_MODEL_FUNC.get(user_role)[2](detail, db)
        return {
            "success": True,
            "id": to_create.id}
    except Exception as err:
        return err.args


def read_from_csv(csv_name):
    with open(csv_name, encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t', skipinitialspace=False)
        list_result_parse = list()
        for row in reader:
            list_result_parse.append(UserFromCsv.parse_obj(row))
    return list_result_parse


def search(mail, md: Base, db: Session):
    return db.query(md).filter(md.email == mail).first()


def find_user_by_email(email, db: Session, role=None, return_role=None):
    if role is None:
        for value in DICT_ROLE_MODEL_FUNC.values():
            model = value[1]
            search_result = search(email, model, db)
            if search_result is not None:
                return [search_result, value[0]] if return_role is True else search_result
    else:
        model = DICT_ROLE_MODEL_FUNC[role][1]
        search_result = search(email, model, db)
    return search_result


def find_by_name(name, model, db):
    return db.query(model).filter(model.full_name == name).first()


def check_by_email(email, model, db):
    return db.query(exists().where(model.email == email)).scalar()


def check_by_name(name, model, db):
    return db.query(exists().where(model.full_name == name)).scalar()


def check_skills(user: Base, db):
    language_id = get_language_id(user.language, db)
    teacher_id = find_by_name(user.full_name, Teacher, db).id
    skills = find_skills(teacher_id, db)
    for el in skills:
        if el.language == language_id:
            return True
    return False


def check_user_by_name_and_email(name, email, db: Session):
    for value in DICT_ROLE_MODEL_FUNC.values():
        model = value[1]
        search_by_email = check_by_email(email, model, db)
        search_by_name = check_by_name(name, model, db)
        if search_by_email or search_by_name:
            return True
    return False


def find_data_by_id(id, db, model):
    return db.query(model).filter(model.id == id).first()


def find_skills(teacher_id, db):
    return db.query(Skills).filter(Skills.teacher == teacher_id).all()


def teachers_list(db: Session, language=None):
    res_list = list()
    if language is None:
        skill_search = db.query(Skills).all()
    else:
        id_language = get_language_id(language, db)
        skill_search = db.query(Skills).filter(Skills.language == id_language)
    for el in skill_search:
        res_list.append(find_data_by_id(el.teacher, db, Teacher))
    return res_list


def student_list(db: Session):
    model = Student
    search_result = db.query(model).all()
    return None if search_result is None else search_result


def find_user_by_token(token, role, db: Session):
    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    try:
        checking_for_access_rights(token, role)
        token_role = payload.get("role")
        email = payload.get("email")
        return find_user_by_email(email, db, token_role)
    except Exception as err:
        raise err


def checking_for_access_rights(token, role):
    if role != jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM).get("role"):
        raise Exception('registered user does not have the right to this action')


def check_to_date_param(from_date, to_date):
    if to_date is not None and datetime.strptime(to_date, '%Y-%m-%d') < datetime.strptime(from_date, '%Y-%m-%d'):
        raise Exception('invalid to_date parameter')
    return from_date if to_date is None else to_date


def check_timetable(user, role, db: Session, from_date, to_date=None):
    dict_student_teacher = \
        {
            "student": Timetable.student,
            "teacher": Timetable.teacher
        }
    md = Timetable
    to_date = check_to_date_param(from_date, to_date)
    return db.query(md).filter(dict_student_teacher.get(role) == user, md.day >= from_date, md.day <= to_date).order_by(
        md.day.asc()).all()


def get_timetable(token, db, role, from_date, to_date):
    user = find_user_by_token(token, role, db)
    timetable = check_timetable(user.id, role, db, from_date, to_date)
    return timetable


def cancel_lesson(date, role, db: Session, token):
    try:
        dict_user_teacher = {
            "student": Student.id,
            "teacher": Teacher.id
        }
        find_user_by_token(token, role, db)
        timetable = check_timetable(dict_user_teacher.get(role), role, db, from_date=date)
        if len(timetable) < 1:
            return 'there were no classes scheduled that day'
        delete_in_db(timetable[0], db)
        delete_by_id(timetable[0].id, Timetable, db)
        return date + ' is free'
    except Exception as err:
        return err.args


def set_users(model, db, language=None):
    data = dict()
    if model == Teacher:
        user_list = teachers_list(db, language)
    if model == Student:
        user_list = student_list(db)
    for el in user_list:
        data[el.email] = el.full_name
    return data


def timetable_list(db, from_date=None, to_date=None):
    model = Timetable
    if from_date is not None:
        to_date = check_to_date_param(from_date, to_date)
        timetable = db.query(model).filter(model.day >= from_date, model.day <= to_date).order_by(model.day.asc()).all()
    else:
        timetable = db.query(model).order_by(model.day.asc()).all()
    return timetable


def schedule_statistics(db, from_date, to_date):
    classes = timetable_list(db, from_date, to_date)
    teachers_classes = dict()
    for el in classes:
        teacher_id = el.teacher
        if teacher_id in teachers_classes:
            teachers_classes[teacher_id] += 1
        else:
            teachers_classes[teacher_id] = 1
    return teachers_classes
