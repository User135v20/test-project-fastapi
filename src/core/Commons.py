import csv
from datetime import datetime

from jose import jwt
from sqlalchemy import exists
from sqlalchemy.orm import Session
from core.security import SECRET_KEY, ALGORITHM, checking_for_access_rights
from db.database import Base
from models import Admin, Student, Teacher
from schemas import UserFromCsv

DICT_ROLE_MODEL = \
    {"admin": ["admin", Admin],
     "student": ["student", Student],
     "teacher": ["teacher", Teacher]
     }


def add_into_db(data: Base, db):
    db.add(data)
    db.commit()


def delete_in_db(data, db: Session):
    db.delete(data)
    db.commit()


def delete_by_id(id, model, db):
    db.query(model).filter_by(id=id).delete(synchronize_session=False)
    db.commit()


def find_data_by_id(id, db, model):
    return db.query(model).filter(model.id == id).first()


def search(mail, md: Base, db: Session):
    return db.query(md).filter(md.email == mail).first()


def check_by_email_and_model(email, model, db):
    return db.query(exists().where(model.email == email)).scalar()


def check_by_name_and_model(name, model, db):
    return db.query(exists().where(model.full_name == name)).scalar()


def check_to_date_param(from_date, to_date):
    if to_date is not None and datetime.strptime(to_date, '%Y-%m-%d') < datetime.strptime(from_date, '%Y-%m-%d'):
        raise Exception('invalid to_date parameter')
    return from_date if to_date is None else to_date


def find_by_name(name, model, db):
    return db.query(model).filter(model.full_name == name).first()


def check_by_name(name, db: Session):
    for value in DICT_ROLE_MODEL.values():
        model = value[1]
        search_by_name = check_by_name_and_model(name, model, db)
        if search_by_name:
            return True
    return False


def check_user_by_email(email, db: Session):
    for value in DICT_ROLE_MODEL.values():
        model = value[1]
        search_by_email = check_by_email_and_model(email, model, db)
        if search_by_email:
            return True
    return False


def find_user_by_email(email, db: Session, role=None, return_role=None):
    if role is None:
        for value in DICT_ROLE_MODEL.values():
            model = value[1]
            search_result = search(email, model, db)
            if search_result is not None:
                return [search_result, value[0]] if return_role is True else search_result
    else:
        model = DICT_ROLE_MODEL[role][1]
        search_result = search(email, model, db)
    return search_result


def find_user_by_token(token, role, db: Session):
    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    try:
        checking_for_access_rights(token, role)
        token_role = payload.get("role")
        email = payload.get("email")
        return find_user_by_email(email, db, token_role)
    except Exception as err:
        raise err


def create_full_name(obj: UserFromCsv):
    return str(obj.last_name) + " " + str(obj.first_name) + " " + str(obj.fatherland)


def read_from_csv(csv_name):
    with open(csv_name,  newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        list_result_parse = list()
        for row in reader:
            list_result_parse.append(UserFromCsv.parse_obj(row))
    return list_result_parse
