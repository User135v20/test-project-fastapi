from fastapi import Depends
from sqlalchemy.orm import Session
from core.logic import oauth2_scheme, find_user_by_token, set_users, timetable_list, schedule_statistics, teachers_list, \
    student_list
from db.database import get_db
from models import Teacher, Student


def get_list_teachers(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        find_user_by_token(token, 'admin', db)
        return set_users(Teacher, db)
    except Exception as err:
        return err.args


def get_list_students(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        find_user_by_token(token, 'admin', db)
        return set_users(Student, db)
    except Exception as err:
        return err.args


def get_book_list(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        find_user_by_token(token, 'admin', db)
        classes = timetable_list(db)
        all_teachers = teachers_list(db)
        all_student = student_list(db)
        res_list = list()
        for el in classes:
            date = el.day
            teacher_name = all_teachers[el.teacher-1].full_name
            student_name = all_student[el.student-1].full_name
            res_list.append(str(date) + " : " + teacher_name + " - " + student_name)
        return res_list
    except Exception as err:
        return err.args


def teacher_statistic(from_date=None, to_date=None, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        find_user_by_token(token, 'admin', db)
        teachers_classes = schedule_statistics(db, from_date, to_date)
        sorted_teachers_classes = sorted(teachers_classes.items(), key=lambda x: -x[1])
        all_teachers = teachers_list(db)
        res_list = list()
        for el in sorted_teachers_classes:
            teacher_name = all_teachers[el[0]-1].full_name
            count = el[1]
            res_list.append(teacher_name + " - " + str(count))
        return res_list
    except Exception as err:
        return err.args
