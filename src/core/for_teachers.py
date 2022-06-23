from fastapi import Depends
from sqlalchemy.orm import Session
from core.logic import find_user_by_email, get_timetable, find_user_by_token, create_teacher, oauth2_scheme, \
    cancel_lesson, get_teacher_by_email_and_lang, delete_by_id
from db.database import get_db
from models import Teacher
from schemas import CreateUserReuest


def list_of_classes_for_teacher(from_date, to_date=None, db: Session = Depends(get_db),
                                token: str = Depends(oauth2_scheme)):
    try:
        timetable = get_timetable(token, db, 'teacher', from_date, to_date)
        if len(timetable) < 1:
            return 'this date is free or these dates are free'
        timetable_res_list = list()
        for el in timetable:
            student = find_user_by_email(el.student, db, 'student').full_name
            timetable_res_list.append(str(el.day) + "  " + str(student))
        return timetable_res_list
    except Exception as err:
        return err.args


def add_language(language, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        teacher = find_user_by_token(token, 'teacher', db)
        if get_teacher_by_email_and_lang(teacher.email, language, db) is not None:
            return "language was previously added for the teacher"
        new_teacher = CreateUserReuest(
            full_name=teacher.full_name,
            email=teacher.email,
            password=teacher.password,
            language=language,
            role='teacher'
        )
        to_create = create_teacher(new_teacher, db)
        return {
            "success": True,
            "id": to_create.id}
    except Exception as err:
        return err.args


def remove_language(language, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        teacher = find_user_by_token(token, 'teacher', db)
        found_teacher = get_teacher_by_email_and_lang(teacher.email, language, db)
        if found_teacher is not None:
            delete_by_id(found_teacher.id, Teacher, db)
            return {"success": True}
        else:
            return "this language was not found"

    except Exception as err:
        return err.args


def cancel_a_booked_lesson_teacher(date, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return cancel_lesson(date, 'teacher', db, token)
