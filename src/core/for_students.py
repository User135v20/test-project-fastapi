from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from core.logic import find_user_by_email, teachers_list, get_language, \
    find_user_by_token, check_timetable, \
    create_schedule_entry, get_timetable, oauth2_scheme, cancel_lesson
from db.database import get_db


def to_book(date, teacher: EmailStr, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        student = find_user_by_token(token, 'student', db).email
        if len(check_timetable(teacher, 'teacher', db, date)) > 0 or len(check_timetable(student, 'student', db, date)) > 0:
            return 'teacher or student is busy on this day'
        to_create = create_schedule_entry(student, teacher, date, db)
        return {
            "success": True,
            "id": to_create.id}
    except Exception as err:
        return err.args


def list_of_classes_for_student(from_date, to_date=None, db: Session = Depends(get_db),
                                token: str = Depends(oauth2_scheme)):
    try:
        timetable = get_timetable(token, db, 'student', from_date, to_date)
        if len(timetable) < 1:
            return 'this date is free or these dates are free'
        timetable_res_list = list()
        for el in timetable:
            teacher = find_user_by_email(el.teacher, db, 'teacher').full_name
            timetable_res_list.append(str(el.day) + "  " + str(teacher))
        return timetable_res_list
    except Exception as err:
        return err.args


def cancel_a_booked_lesson_student(date, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return cancel_lesson(date, 'student', db, token)


def find_free_teachers(from_date, to_date=None, language=None, db: Session = Depends(get_db),
                       token: str = Depends(oauth2_scheme)):
    try:
        find_user_by_token(token, "student", db)
        list_teachers = teachers_list(db, language)
        list_free_teachers = list()
        for el in list_teachers:
            lessons_for_the_specified_dates = check_timetable(el.email, 'teacher', db, from_date, to_date)
            if len(lessons_for_the_specified_dates) < 1:
                if language is None:
                    teacher_language = get_language(db, el.language)
                    list_free_teachers.append(el.full_name + " | " + teacher_language)
                else:
                    list_free_teachers.append(el.full_name)
        return list_free_teachers
    except Exception as err:
        return err.args
