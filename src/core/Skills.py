from fastapi import Depends
from sqlalchemy import exists
from sqlalchemy.orm import Session
from core.Commons import add_into_db, find_by_name, delete_by_id, find_user_by_token
from core.Language import get_language_id, add_language_to_db
from core.security import oauth2_scheme
from db.database import Base, get_db
from models import Skills, Teacher


def find_skills(teacher_id, db):
    return db.query(Skills).filter(Skills.teacher == teacher_id).all()


def add_skill_in_db(db, teacher_id, language_id):
    data = Skills(
        teacher=teacher_id,
        language=language_id
    )
    add_into_db(data, db)
    return data.id

def check_skills(teacher_id, language_id,  db):
    if teacher_id is None or language_id is None:
        return False
    return db.query(exists().where(Skills.teacher == teacher_id and Skills.language == language_id)).scalar()


def add_skills(user, language, db):
    teacher = find_by_name(user.full_name, Teacher, db)
    if teacher is not None:
        teacher_id = teacher.id
        language_id = get_language_id(language, db)
        if not check_skills(teacher_id, language_id, db):
            if language_id is None:
                language_id = add_language_to_db(language, db)
            return add_skill_in_db(db, teacher_id, language_id)


def add_language(language, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        teacher = find_user_by_token(token, 'teacher', db)
        skill_id = add_skills(teacher, language, db)
        if skill_id is None:
            return "language was previously added for the teacher"
        return {
            "success": True,
            "skill id": skill_id}
    except Exception as err:
        return err.args


def remove_language(language, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        teacher_id = find_user_by_token(token, 'teacher', db).id
        language_id = get_language_id(language, db)
        skills = find_skills(teacher_id, db)
        for skill in skills:
            if language_id == skill.language:
                delete_by_id(skill.id, Skills, db)
                return {"success": True
                        }
        return "this language was not found"
    except Exception as err:
        return err.args