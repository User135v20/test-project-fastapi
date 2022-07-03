from fastapi import Depends
from sqlalchemy import exists
from sqlalchemy.orm import Session
from core.Commons import add_into_db, find_by_name, delete_by_id, find_user_by_token
from core.Language import get_language_id, add_language_to_db
from core.security import oauth2_scheme, checking_for_access_rights
from db.database import get_db
from models import Skills, Teacher


def find_skills(teacher_id, db_connect):
    return db_connect.query(Skills).filter(Skills.teacher == teacher_id).all()


def add_skill_in_db(db_connect, teacher_id, language_id):
    data = Skills(teacher=teacher_id, language=language_id)
    add_into_db(data, db_connect)
    return data.id


def check_skills(teacher_id, language_id, db_connect):
    if teacher_id is None or language_id is None:
        return False
    return db_connect.query(
        exists().where(Skills.teacher == teacher_id, Skills.language == language_id)
    ).scalar()


def add_skills(user, language, db_connect):
    teacher = find_by_name(user.full_name, Teacher, db_connect)
    if teacher is not None:
        teacher_id = teacher.id
        language_id = get_language_id(language, db_connect)
        if not check_skills(teacher_id, language_id, db_connect):
            if language_id is None:
                language_id = add_language_to_db(language, db_connect)
            return add_skill_in_db(db_connect, teacher_id, language_id)


def add_language_by_teacher(
    language, db_connect: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        checking_for_access_rights(token, "teacher")
        teacher = find_user_by_token(token, db_connect)
        skill_id = add_skills(teacher, language, db_connect)
        if skill_id is None:
            return "language was previously added for the teacher"
        return {"success": True, "skill id": skill_id}
    except Exception as err:
        raise err


def remove_language_by_teacher(
    language, db_connect: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        checking_for_access_rights(token, "teacher")
        teacher_id = find_user_by_token(token, db_connect).id
        language_id = get_language_id(language, db_connect)
        skills = find_skills(teacher_id, db_connect)
        for skill in skills:
            if language_id == skill.language:
                delete_by_id(skill.id, Skills, db_connect)
                return {"success": True}
        return "this language was not found"
    except Exception as err:
        raise err
