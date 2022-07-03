from datetime import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from core.Commons import (
    add_into_db,
    delete_in_db,
    delete_by_id,
    find_data_by_id,
    find_by_name,
    check_to_date_param,
    find_user_by_token,
)
from core.Student import student_list
from core.Teacher import teachers_list
from core.security import oauth2_scheme, checking_for_access_rights
from db.database import get_db
from models import Timetable, Student, Teacher

MODEL = Timetable
TMAX = 2
SMAX = 4


def check_timetable(user, role, db_connect: Session, from_date, to_date=None):
    try:
        dict_student_teacher = {
            "student": Timetable.student,
            "teacher": Timetable.teacher,
        }
        to_date = check_to_date_param(from_date, to_date)
        return (
            db_connect.query(MODEL)
            .filter(
                dict_student_teacher.get(role) == user,
                MODEL.day >= from_date,
                MODEL.day <= to_date,
            )
            .order_by(MODEL.day.asc())
            .all()
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid date params")


def create_schedule_entry(student, teacher, day, db_connect):
    data = Timetable(
        student=student, teacher=teacher, day=datetime.strptime(day, "%Y-%m-%d")
    )
    add_into_db(data, db_connect)
    return data


def check_smax(user, db_connect):
    return db_connect.query(MODEL).filter(MODEL.student == user).count()


def check_tmax(user, db_connect):
    return db_connect.query(MODEL).filter(MODEL.teacher == user).count()


def to_book(
    date,
    teacher_name,
    db_connect: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        checking_for_access_rights(token, "student")
        student = find_user_by_token(token, db_connect)
        student_id = student.id
        found_teacher = find_by_name(teacher_name, Teacher, db_connect)
        if found_teacher is None:
            return "teacher with this name was not found"
        teacher_id = found_teacher.id
        if (
            len(check_timetable(teacher_id, "teacher", db_connect, date)) > 0
            or len(check_timetable(student_id, "student", db_connect, date)) > 0
        ):
            return "teacher or student is busy on this day"
        if check_tmax(teacher_id, db_connect) >= TMAX:
            return "teacher's schedule contains the maximum number of classes"
        if check_smax(student_id, db_connect) >= SMAX:
            return "student's schedule contains the maximum number of classes"
        to_create = create_schedule_entry(student_id, teacher_id, date, db_connect)
        return {"success": True, "id": to_create.id}
    except Exception as err:
        return err


def get_timetable(token, db_connect, role, from_date, to_date):
    user = find_user_by_token(token, db_connect)
    timetable = check_timetable(user.id, role, db_connect, from_date, to_date)
    return timetable


def list_of_classes_for_teacher(
    from_date,
    to_date=None,
    db_connect: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        checking_for_access_rights(token, "teacher")
        timetable = get_timetable(token, db_connect, "teacher", from_date, to_date)
        if len(timetable) < 1:
            return "this date is free or these dates are free"
        timetable_res_list = []
        for lesson in timetable:
            student = find_data_by_id(lesson.student, db_connect, Student).full_name
            timetable_res_list.append(str(lesson.day) + "  " + str(student))
        return timetable_res_list
    except HTTPException as err:
        raise err


def list_of_classes_for_student(
    from_date,
    to_date=None,
    db_connect: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        checking_for_access_rights(token, "student")
        timetable = get_timetable(token, db_connect, "student", from_date, to_date)
        if len(timetable) < 1:
            return "this date is free or these dates are free"
        timetable_res_list = []
        for lesson in timetable:
            teacher = find_data_by_id(lesson.teacher, db_connect, Teacher).full_name
            timetable_res_list.append(str(lesson.day) + "  " + str(teacher))
        return timetable_res_list
    except Exception as err:
        return HTTPException(status_code=401, detail=err.args)


def cancel_lesson(date, role, db_connect: Session, token):
    try:
        dict_user_teacher = {"student": Student.id, "teacher": Teacher.id}
        checking_for_access_rights(token, role)
        timetable = check_timetable(
            dict_user_teacher.get(role), role, db_connect, from_date=date
        )
        if len(timetable) < 1:
            return "there were no classes scheduled that day"
        delete_in_db(timetable[0], db_connect)
        delete_by_id(timetable[0].id, Timetable, db_connect)
        return date + " is free"
    except Exception as err:
        raise err


def cancel_lesson_by_teacher(
    date, db_connect: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        return cancel_lesson(date, "teacher", db_connect, token)
    except Exception as err:
        raise err


def cancel_lesson_by_student(
    date, db_connect: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        return cancel_lesson(date, "student", db_connect, token)
    except Exception as err:
        return err


def find_free_teachers(
    from_date,
    to_date=None,
    language=None,
    db_connect: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        checking_for_access_rights(token, "student")
        list_teachers = teachers_list(db_connect, language)
        list_free_teachers = []
        for teacher in list_teachers:
            lessons_in_dates = check_timetable(
                teacher.id, "teacher", db_connect, from_date, to_date
            )
            if len(lessons_in_dates) < 1:
                list_free_teachers.append(teacher.full_name)
        if len(list_free_teachers) < 1:
            return "there are no available teachers for this date or date interval"
        return list_free_teachers
    except HTTPException as err:
        return err


def timetable_list(db_connect, from_date=None, to_date=None):
    if from_date is not None:
        to_date = check_to_date_param(from_date, to_date)
        timetable = (
            db_connect.query(MODEL)
            .filter(MODEL.day >= from_date, MODEL.day <= to_date)
            .order_by(MODEL.day.asc())
            .all()
        )
    else:
        timetable = db_connect.query(MODEL).order_by(MODEL.day.asc()).all()
    return timetable


def get_book_list(
    db_connect: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    try:
        checking_for_access_rights(token, "admin")
        classes = timetable_list(db_connect)
        all_teachers = teachers_list(db_connect)
        all_student = student_list(db_connect)
        res_list = []
        for lesson in classes:
            date = lesson.day
            teacher_name = all_teachers[lesson.teacher - 1].full_name
            student_name = all_student[lesson.student - 1].full_name
            res_list.append(str(date) + " : " + teacher_name + " - " + student_name)
        return res_list
    except Exception as err:
        return err


def schedule_statistics(db_connect, from_date, to_date):
    classes = timetable_list(db_connect, from_date, to_date)
    teachers_classes = {}
    for lesson in classes:
        teacher_id = lesson.teacher
        if teacher_id in teachers_classes:
            teachers_classes[teacher_id] += 1
        else:
            teachers_classes[teacher_id] = 1
    return teachers_classes


def teacher_statistic_for_admin(
    from_date=None,
    to_date=None,
    db_connect: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    try:
        checking_for_access_rights(token, "admin")
        teachers_classes = schedule_statistics(db_connect, from_date, to_date)
        sorted_teachers_classes = sorted(teachers_classes.items(), key=lambda x: -x[1])
        all_teachers = teachers_list(db_connect)
        res_list = []
        for lesson in sorted_teachers_classes:
            teacher_name = all_teachers[lesson[0] - 1].full_name
            count = lesson[1]
            res_list.append(teacher_name + " - " + str(count))
        return res_list
    except Exception as err:
        return err
