from fastapi import Depends
from sqlalchemy.orm import Session
from core.Commons import add_into_db, find_data_by_id, find_user_by_token, read_from_csv, create_full_name, \
    check_by_name
from core.Language import get_language_id, add_language_to_db
from core.Skills import add_skill_in_db, add_skills
from core.security import hash_password, oauth2_scheme
from db.database import get_db
from models import Teacher, Skills
from schemas import CreateUserReuest


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
    user.skills = add_skill_in_db(db, user.id, language_id)
    db.commit()
    return user


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


def get_list_teachers(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        find_user_by_token(token, 'admin', db)
        res_list = list()
        for el in teachers_list(db):
            res_list.append(el.full_name)
        return res_list if len(res_list) > 1 else "list of teachers is empty"
    except Exception as err:
        return err.args


def add_teacher_from_scv_file(file_name, db):
    count_added = 0
    count_updated = 0
    list_result_parse = read_from_csv(file_name)
    for el in list_result_parse:

        full_name = create_full_name(el)
        if el.language == "":
            language = None
        else:
            language = el.language
        user = CreateUserReuest(
            full_name=full_name,
            language=language)
        if check_by_name(user.full_name, db):
            if add_skills(user, language, db) is not None:
                count_updated += 1
        else:
            create_teacher(user, db)
            count_added += 1
    return {"success": True,
            "number of added teachers": count_added,
            "number of updated teachers": count_updated}
