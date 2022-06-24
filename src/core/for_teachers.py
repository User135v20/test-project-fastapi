from fastapi import Depends
from sqlalchemy.orm import Session
from core.logic import get_timetable, find_user_by_token, oauth2_scheme, \
    cancel_lesson, delete_by_id, find_data_by_id, find_skills, get_language_id, add_skill, add_language_to_db
from db.database import get_db
from models import Student, Skills


def list_of_classes_for_teacher(from_date, to_date=None, db: Session = Depends(get_db),
                                token: str = Depends(oauth2_scheme)):
    try:
        timetable = get_timetable(token, db, 'teacher', from_date, to_date)
        if len(timetable) < 1:
            return 'this date is free or these dates are free'
        timetable_res_list = list()
        for el in timetable:
            student = find_data_by_id(el.student, db, Student).full_name
            timetable_res_list.append(str(el.day) + "  " + str(student))
        return timetable_res_list
    except Exception as err:
        return err.args


def add_language(language, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        teacher_id = find_user_by_token(token, 'teacher', db).id
        language_id = get_language_id(language, db)
        if language_id is None:
            language_id = add_language_to_db(language, db)
        skills = find_skills(teacher_id, db)
        for skill in skills:
            if language_id == skill.language:
                return "language was previously added for the teacher"
        to_create = add_skill(db, teacher_id, language_id)
        return {
            "success": True,
            "id": to_create}
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


def cancel_a_booked_lesson_teacher(date, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return cancel_lesson(date, 'teacher', db, token)
