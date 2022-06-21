from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from core.logic import find_user_by_email, delete_in_db, teachers_list, get_language, \
    find_user_by_token, check_timetable, \
    create_schedule_entry, get_timetable, oauth2_scheme
from db.database import get_db


def to_book(date, teacher: EmailStr, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    student = find_user_by_token(token, 'student', db)
    if student is None:
        return 'user does not have access'
    if len(check_timetable(teacher, 'teacher', db, date)) < 1 or len(check_timetable(student, 'student', db, date)) < 1:
        return 'teacher or student is busy on this day'
    try:
        to_create = create_schedule_entry(student[0].email, teacher, date, db)
        return {
            "success": True,
            "id": to_create.id}
    except:
        return 'Failed attempt to add an entry to the schedule'


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


def cancel_a_booked_lesson(date, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    student = find_user_by_token(token, 'student', db)
    timetable = check_timetable(student.email, 'student', db, date)
    if len(timetable) < 1:
        return 'this date is free'
    delete_in_db(timetable[0], db)
    return date + ' is free'


def find_free_teachers(from_date, to_date=None, language=None, db: Session = Depends(get_db),
                       token: str = Depends(oauth2_scheme)):
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
