from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.Admin import create_admin
from core.Commons import check_by_name, check_user_by_email, find_user_by_email
from core.Skills import add_language_by_teacher, remove_language_by_teacher
from core.Student import create_student, add_student_from_scv_file, get_students_for_admin
from core.Teacher import create_teacher, add_teacher_from_scv_file, get_teachers_for_admin
from core.Timetable import to_book, list_of_classes_for_student, find_free_teachers, \
    teacher_statistic_for_admin, list_of_classes_for_teacher, get_book_list, \
    cancel_lesson_by_teacher, cancel_lesson_by_student
from core.security import password_verification, create_access_token
from db.database import get_db
from schemas import CreateUserReuest, Token

TEACHER_FILE = "teacher.csv"
STUDENT_FILE = "student.csv"
app = FastAPI()


@app.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_users(detail: CreateUserReuest, db_connect: Session = Depends(get_db)):
    """create_users"""
    dict_role_func = {
        "admin": create_admin,
        "student": create_student,
        "teacher": create_teacher
    }
    user_email = detail.email
    user_name = detail.full_name
    user_role = detail.role
    if check_by_name(user_name, db_connect):
        return 'user with this name already exists'
    if check_user_by_email(user_email, db_connect):
        return 'user with this email already exists'
    try:
        to_create = dict_role_func.get(user_role)(detail, db_connect)
        return {
            "success": True,
            "id": to_create.id}
    except Exception as err:
        return err.args


@app.post('/token', response_model=Token, status_code=status.HTTP_201_CREATED)
async def login(db_connect: Session = Depends(get_db),
                detail: OAuth2PasswordRequestForm = Depends()):
    """login users by email and password"""
    try:
        user_and_role_by_email = find_user_by_email(detail.username,
                                                    db_connect, return_role=True)
        if user_and_role_by_email is None:
            raise
        user = user_and_role_by_email[0]
        user_role = user_and_role_by_email[1]
        if not password_verification(detail.password, user.password):
            return HTTPException(status_code=401, detail='Invalid password')
        access_token = create_access_token({"role": user_role, "email": user.email})
        return {'access_token': access_token, "token_type": "bearer", }
    except HTTPException:
        return HTTPException(status_code=401, detail='Invalid email')


@app.post("/add_teacher_from_csv", status_code=status.HTTP_201_CREATED, tags=["add from csv"])
def add_teacher_from_csv(db_connect: Session = Depends(get_db)):
    """add_teacher_from_csv"""
    return add_teacher_from_scv_file(TEACHER_FILE, db_connect)


@app.post("/add_student_from_csv", status_code=status.HTTP_201_CREATED, tags=["add from csv"])
def add_student_from_csv(db_connect: Session = Depends(get_db)):
    """add_student_from_csv"""
    return add_student_from_scv_file(STUDENT_FILE, db_connect)


@app.post('/student/to_book', status_code=status.HTTP_201_CREATED, tags=["student"])
async def make_an_appointments(user: CreateUserReuest = Depends(to_book)):
    """student signs up for a lesson with a teacher"""
    try:
        return user
    except Exception as err:
        return err


@app.get('/student/list_of_classes', status_code=status.HTTP_200_OK, tags=["student"])
async def list_students_classes(user: CreateUserReuest = Depends(list_of_classes_for_student)):
    """list student's classes"""
    return user


@app.delete('/student/cancel_lesson', status_code=status.HTTP_200_OK, tags=["student"])
async def cancel_lesson_for_student(user: CreateUserReuest = Depends(cancel_lesson_by_student)):
    """cancel lesson for student"""
    return user


@app.get('/student/free_teacher', status_code=status.HTTP_200_OK, tags=["student"])
async def list_of_available_teachers(list_classes: CreateUserReuest = Depends(find_free_teachers)):
    """list_of_available_teachers"""
    try:
        return list_classes
    except Exception as err:
        return err


@app.get('/teacher/list_of_classes', status_code=status.HTTP_200_OK, tags=["teacher"])
async def list_teachers_classes(classes: CreateUserReuest = Depends(list_of_classes_for_teacher)):
    """list_teachers_classes"""
    return classes


@app.post('/teacher/add_language', status_code=status.HTTP_201_CREATED, tags=["teacher"])
async def add_languages(result: CreateUserReuest = Depends(add_language_by_teacher)):
    """add language for teacher"""
    return result


@app.delete('/teacher/remove_language', status_code=status.HTTP_200_OK, tags=["teacher"])
async def remove_languages(result: CreateUserReuest = Depends(remove_language_by_teacher)):
    """remove languages for teacher"""
    return result


@app.delete('/teacher/cancel_lesson', status_code=status.HTTP_200_OK, tags=["teacher"])
async def cancel_lesson_for_teacher(result: CreateUserReuest = Depends(cancel_lesson_by_teacher)):
    """cancel lesson for teacher"""
    return result


@app.get('/admin/list_teachers', status_code=status.HTTP_200_OK, tags=["admin"])
async def list_teachers(users: CreateUserReuest = Depends(get_teachers_for_admin)):
    """list teachers for admin"""
    return users


@app.get('/admin/list_students', status_code=status.HTTP_200_OK, tags=["admin"])
async def list_students(users: CreateUserReuest = Depends(get_students_for_admin)):
    """list students for admin"""
    return users


@app.get('/admin/books', status_code=status.HTTP_200_OK, tags=["admin"])
async def list_books(timetable: CreateUserReuest = Depends(get_book_list)):
    """return timetable"""
    return timetable


@app.get('/admin/statistics', status_code=status.HTTP_200_OK, tags=["admin"])
async def statistic(data: CreateUserReuest = Depends(teacher_statistic_for_admin)):
    """returns lesson statistics for teachers"""
    return data
