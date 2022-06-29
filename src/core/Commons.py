import csv
from datetime import datetime
from jose import jwt
from sqlalchemy import exists
from core.security import SECRET_KEY, ALGORITHM
from db.database import Base
from models import Admin, Student, Teacher
from schemas import UserFromCsv

DICT_ROLE_MODEL = {
    "admin": ["admin", Admin],
    "student": ["student", Student],
    "teacher": ["teacher", Teacher],
}


def add_into_db(data: Base, db_connect):
    db_connect.add(data)
    db_connect.commit()


def delete_in_db(data, db_connect):
    db_connect.delete(data)
    db_connect.commit()


def delete_by_id(data_id, model, db_connect):
    db_connect.query(model).filter_by(id=data_id).delete(synchronize_session=False)
    db_connect.commit()


def find_data_by_id(data_id, db_connect, model):
    return db_connect.query(model).filter(model.id == data_id).first()


def search(mail, model: Base, db_connect):
    return db_connect.query(model).filter(model.email == mail).first()


def check_by_email_and_model(email, model, db_connect):
    return db_connect.query(exists().where(model.email == email)).scalar()


def check_by_name_and_model(name, model, db_connect):
    return db_connect.query(exists().where(model.full_name == name)).scalar()


def check_to_date_param(from_date, to_date):
    if to_date is not None and datetime.strptime(
        to_date, "%Y-%m-%d"
    ) < datetime.strptime(from_date, "%Y-%m-%d"):
        raise Exception("invalid to_date parameter")
    return from_date if to_date is None else to_date


def find_by_name(name, model, db_connect):
    return db_connect.query(model).filter(model.full_name == name).first()


def check_by_name(name, db_connect):
    for value in DICT_ROLE_MODEL.values():
        model = value[1]
        search_by_name = check_by_name_and_model(name, model, db_connect)
        if search_by_name:
            return True
    return False


def check_user_by_email(email, db_connect):
    for value in DICT_ROLE_MODEL.values():
        model = value[1]
        search_by_email = check_by_email_and_model(email, model, db_connect)
        if search_by_email:
            return True
    return False


def find_user_by_email(email, db_connect, role=None, return_role=None):
    search_result = None
    if role is None:
        for value in DICT_ROLE_MODEL.values():
            model = value[1]
            search_result = search(email, model, db_connect)
            if search_result is not None:
                return (
                    [search_result, value[0]] if return_role is True else search_result
                )
    else:
        model = DICT_ROLE_MODEL[role][1]
        search_result = search(email, model, db_connect)
    return search_result


def find_user_by_token(token, db_connect):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        token_role = payload.get("role")
        email = payload.get("email")
        return find_user_by_email(email, db_connect, token_role)
    except Exception as err:
        return err


def create_full_name(obj: UserFromCsv):
    return str(obj.last_name) + " " + str(obj.first_name) + " " + str(obj.fatherland)


def read_from_csv(csv_name):
    with open(csv_name, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")
        list_result_parse = []
        for row in reader:
            list_result_parse.append(UserFromCsv.parse_obj(row))
    return list_result_parse
