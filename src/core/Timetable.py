from datetime import datetime
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from core.Commons import add_into_db, delete_in_db, delete_by_id, find_data_by_id, find_user_by_token, find_user_by_email, \
    find_by_name, check_to_date_param
from core.Student import student_list
from core.Teacher import teachers_list
from core.security import oauth2_scheme
from db.database import get_db
from models import Timetable, Student, Teacher


def check_timetable(user, role, db: Session, from_date, to_date=None):
    dict_student_teacher = \
        {
            "student": Timetable.student,
            "teacher": Timetable.teacher
        }
    md = Timetable
    to_date = check_to_date_param(from_date, to_date)
    return db.query(md).filter(dict_student_teacher.get(role) == user, md.day >= from_date, md.day <= to_date).order_by(
        md.day.asc()).all()


def create_schedule_entry(student, teacher, day, db):
    data = Timetable(
        student=student,
        teacher=teacher,
        day=datetime.strptime(day, '%Y-%m-%d'))
    add_into_db(data, db)
    return data


def to_book(date, teacher, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        student_id = find_user_by_token(token, 'student', db).id
        found_teacher = find_by_name(teacher,Teacher, db)
        if found_teacher is None:
            return 'teacher with this email was not found'
        teacher_id = found_teacher.id
        if len(check_timetable(teacher_id, 'teacher', db, date)) > 0 or len(
                check_timetable(student_id, 'student', db, date)) > 0:
            return 'teacher or student is busy on this day'
        to_create = create_schedule_entry(student_id, teacher_id, date, db)
        return {
            "success": True,
            "id": to_create.id}
    except Exception as err:
        return err.args


def get_timetable(token, db, role, from_date, to_date):
    user = find_user_by_token(token, role, db)
    timetable = check_timetable(user.id, role, db, from_date, to_date)
    return timetable


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


def list_of_classes_for_student(from_date, to_date=None, db: Session = Depends(get_db),
                                token: str = Depends(oauth2_scheme)):
    try:
        timetable = get_timetable(token, db, 'student', from_date, to_date)
        if len(timetable) < 1:
            return 'this date is free or these dates are free'
        timetable_res_list = list()
        for el in timetable:
            teacher = find_data_by_id(el.teacher, db, Teacher).full_name
            timetable_res_list.append(str(el.day) + "  " + str(teacher))
        return timetable_res_list
    except Exception as err:
        return HTTPException(status_code=401, detail=err.args)


def cancel_lesson(date, role, db: Session, token):
    try:
        dict_user_teacher = {
            "student": Student.id,
            "teacher": Teacher.id
        }
        find_user_by_token(token, role, db)
        timetable = check_timetable(dict_user_teacher.get(role), role, db, from_date=date)
        if len(timetable) < 1:
            return 'there were no classes scheduled that day'
        delete_in_db(timetable[0], db)
        delete_by_id(timetable[0].id, Timetable, db)
        return date + ' is free'
    except Exception as err:
        return err.args


def cancel_a_booked_lesson_teacher(date, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return cancel_lesson(date, 'teacher', db, token)


def cancel_a_booked_lesson_student(date, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    return cancel_lesson(date, 'student', db, token)


def find_free_teachers(from_date, to_date=None, language=None, db: Session = Depends(get_db),
                       token: str = Depends(oauth2_scheme)):
    try:
        find_user_by_token(token, "student", db)
        list_teachers = teachers_list(db, language)
        list_free_teachers = list()
        for el in list_teachers:
            lessons_for_the_specified_dates = check_timetable(el.id, 'teacher', db, from_date, to_date)
            if len(lessons_for_the_specified_dates) < 1:
                list_free_teachers.append(str(el.full_name) + " : " + str(el.email))
        if len(list_free_teachers) < 1:
            return 'there are no available teachers for this date\date interval'
        return list_free_teachers
    except Exception as err:
        return err.args


def timetable_list(db, from_date=None, to_date=None):
    model = Timetable
    if from_date is not None:
        to_date = check_to_date_param(from_date, to_date)
        timetable = db.query(model).filter(model.day >= from_date, model.day <= to_date).order_by(model.day.asc()).all()
    else:
        timetable = db.query(model).order_by(model.day.asc()).all()
    return timetable


def get_book_list(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        find_user_by_token(token, 'admin', db)
        classes = timetable_list(db)
        all_teachers = teachers_list(db)
        all_student = student_list(db)
        res_list = list()
        for el in classes:
            date = el.day
            teacher_name = all_teachers[el.teacher - 1].full_name
            student_name = all_student[el.student - 1].full_name
            res_list.append(str(date) + " : " + teacher_name + " - " + student_name)
        return res_list
    except Exception as err:
        return err.args


def schedule_statistics(db, from_date, to_date):
    classes = timetable_list(db, from_date, to_date)
    teachers_classes = dict()
    for el in classes:
        teacher_id = el.teacher
        if teacher_id in teachers_classes:
            teachers_classes[teacher_id] += 1
        else:
            teachers_classes[teacher_id] = 1
    return teachers_classes


def teacher_statistic(from_date=None, to_date=None, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        find_user_by_token(token, 'admin', db)
        teachers_classes = schedule_statistics(db, from_date, to_date)
        sorted_teachers_classes = sorted(teachers_classes.items(), key=lambda x: -x[1])
        all_teachers = teachers_list(db)
        res_list = list()
        for el in sorted_teachers_classes:
            teacher_name = all_teachers[el[0] - 1].full_name
            count = el[1]
            res_list.append(teacher_name + " - " + str(count))
        return res_list
    except Exception as err:
        return err.args
