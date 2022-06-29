from fastapi import Depends
from sqlalchemy.orm import Session
from core.Commons import (
    add_into_db,
    find_data_by_id,
    read_from_csv,
    create_full_name,
    check_by_name,
)
from core.Language import get_language_id, add_language_to_db
from core.Skills import add_skill_in_db, add_skills
from core.security import hash_password, oauth2_scheme, checking_for_access_rights
from db.database import get_db
from models import Teacher, Skills
from schemas import CreateUserReuest


def create_teacher(detail: CreateUserReuest, db_connect):
    if detail.password is None:
        password = detail.password
    else:
        password = hash_password(detail.password)
    user = Teacher(full_name=detail.full_name, email=detail.email, password=password)
    add_into_db(user, db_connect)
    language_id = get_language_id(detail.language, db_connect)
    if language_id is None:
        language_id = add_language_to_db(detail.language, db_connect)
    user.skills = add_skill_in_db(db_connect, user.id, language_id)
    db_connect.commit()
    return user


def teachers_list(db_connect, language=None):
    res_list = []
    if language is None:
        skill_search = db_connect.query(Skills).all()
    else:
        id_language = get_language_id(language, db_connect)
        skill_search = db_connect.query(Skills).filter(Skills.language == id_language)
    for skill in skill_search:
        res_list.append(find_data_by_id(skill.teacher, db_connect, Teacher))
    return res_list


def get_teachers_for_admin(
    db_connect: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        checking_for_access_rights(token, "admin")
        res_list = []
        for teacher in teachers_list(db_connect):
            res_list.append(teacher.full_name)
        return res_list if len(res_list) > 1 else "list of teachers is empty"
    except Exception as err:
        return err


def add_teacher_from_scv_file(file_name, db_connect):
    count_added = 0
    count_updated = 0
    list_result_parse = read_from_csv(file_name)
    for raw_str_teacher in list_result_parse:

        full_name = create_full_name(raw_str_teacher)
        if raw_str_teacher.language == "":
            language = None
        else:
            language = raw_str_teacher.language
        user = CreateUserReuest(full_name=full_name, language=language)
        if check_by_name(user.full_name, db_connect):
            if add_skills(user, language, db_connect) is not None:
                count_updated += 1
        else:
            create_teacher(user, db_connect)
            count_added += 1
    return {
        "success": True,
        "number of added teachers": count_added,
        "number of updated teachers": count_updated,
    }
