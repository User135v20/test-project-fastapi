from fastapi import Depends
from sqlalchemy.orm import Session
from core.logic import find_user_by_email, get_timetable, find_user_by_token, create_teacher, teachers_list, \
    get_language_id, oauth2_scheme
from db.database import get_db
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
        id_language = get_language_id(language, db)
        if id_language is not None:
            teacher_list = teachers_list(db)
            for el in teacher_list:
                if el.email == teacher.email and el.language == id_language:
                    return "this language has already been added to the database"

        new_teacher = CreateUserReuest(
            full_name=teacher.full_name,
            email=teacher.email,
            password=teacher.password,
            language=language,
            role='teacher'
        )
        return {
            "success": True,
            "id": create_teacher(new_teacher, db).id}
    except Exception as err:
        return err.args


