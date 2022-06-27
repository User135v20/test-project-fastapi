from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.Admin import create_admin
# from core.Commons import find_user_by_email, check_by_name, check_by_email
# from core.Skills import add_language, remove_language
# from core.Student import add_student_from_scv_file, get_list_students, create_student
# from core.Teacher import add_teacher_from_scv_file, get_list_teachers, create_teacher
# from core.Timetable import to_book, list_of_classes_for_student, cancel_a_booked_lesson_student, find_free_teachers, \
#     list_of_classes_for_teacher, cancel_a_booked_lesson_teacher, get_book_list, teacher_statistic
# from core.security import password_verification, create_access_token
from core.Commons import check_by_name, check_user_by_email, find_user_by_email
from core.Skills import add_language, remove_language
from core.Student import create_student, get_list_students, add_student_from_scv_file
from core.Teacher import create_teacher, get_list_teachers, add_teacher_from_scv_file
from core.Timetable import to_book, list_of_classes_for_student, cancel_a_booked_lesson_student, find_free_teachers, \
    list_of_classes_for_teacher, cancel_a_booked_lesson_teacher, get_book_list, teacher_statistic
from core.security import password_verification, create_access_token
from db.database import get_db
from schemas import CreateUserReuest, Token

TEACHER_FILE = "teacher.csv"
STUDENT_FILE = "student.csv"
app = FastAPI()



@app.post("/add_teacher_from_csv", status_code=status.HTTP_201_CREATED)
def add_from_csv(db: Session = Depends(get_db)):
    return add_teacher_from_scv_file(TEACHER_FILE, db)


@app.post("/add_student_from_csv", status_code=status.HTTP_201_CREATED)
def add_from_csv(db: Session = Depends(get_db)):
    return add_student_from_scv_file(STUDENT_FILE, db)


@app.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_users(detail: CreateUserReuest, db: Session = Depends(get_db)):
    DICT_ROLE_MODEL_FUNC = \
        {
         "admin": create_admin,
         "student": create_student,
         "teacher": create_teacher
         }
    user_email = detail.email
    user_name = detail.full_name
    user_role = detail.role
    if check_by_name(user_name, db):
        return 'user with this name already exists'
    if check_user_by_email(user_email, db):
        return 'user with this email already exists'
    try:
        to_create = DICT_ROLE_MODEL_FUNC.get(user_role)(detail, db)
        return {
            "success": True,
            "id": to_create.id}
    except Exception as err:
        return err.args


@app.post('/token', response_model=Token, status_code=status.HTTP_201_CREATED)
async def login(db: Session = Depends(get_db), detail: OAuth2PasswordRequestForm = Depends()):
    try:
        user_and_role_by_email = find_user_by_email(detail.username, db, return_role=True)
        if user_and_role_by_email is None:
            raise
        user = user_and_role_by_email[0]
        user_role = user_and_role_by_email[1]
        if not password_verification(detail.password, user.password):
            return HTTPException(status_code=401, detail='Invalid password')
        access_token = create_access_token({"role": user_role, "email": user.email})
        return {'access_token': access_token, "token_type": "bearer", }
    except:
        return HTTPException(status_code=401, detail='Invalid email')


@app.post('/student/to_book', status_code=status.HTTP_201_CREATED, tags=["student"])
async def make_an_appointments(user: CreateUserReuest = Depends(to_book)):
    return user


@app.get('/student/list_of_classes', status_code=status.HTTP_200_OK, tags=["student"])
async def list_of_classes(user: CreateUserReuest = Depends(list_of_classes_for_student)):
    return user


@app.delete('/student/cancel_lesson', status_code=status.HTTP_200_OK, tags=["student"])
async def cancel_lesson(user: CreateUserReuest = Depends(cancel_a_booked_lesson_student)):
    return user


@app.get('/student/free_teacher', status_code=status.HTTP_200_OK, tags=["student"])
async def list_of_available_teachers(list_classes: CreateUserReuest = Depends(find_free_teachers)):
    return list_classes


@app.get('/teacher/list_of_classes', status_code=status.HTTP_200_OK, tags=["teacher"])
async def list_of_available_teachers(list_classes: CreateUserReuest = Depends(list_of_classes_for_teacher)):
    return list_classes


@app.post('/teacher/add_language', status_code=status.HTTP_201_CREATED, tags=["teacher"])
async def add_languages(result: CreateUserReuest = Depends(add_language)):
    return result


@app.delete('/teacher/remove_language', status_code=status.HTTP_200_OK, tags=["teacher"])
async def remove_languages(result: CreateUserReuest = Depends(remove_language)):
    return result


@app.delete('/teacher/cancel_lesson', status_code=status.HTTP_200_OK, tags=["teacher"])
async def cancel_lesson(result: CreateUserReuest = Depends(cancel_a_booked_lesson_teacher)):
    return result


@app.get('/admin/list_teachers', status_code=status.HTTP_200_OK, tags=["admin"])
async def list_teachers(users: CreateUserReuest = Depends(get_list_teachers)):
    return users


@app.get('/admin/list_students', status_code=status.HTTP_200_OK, tags=["admin"])
async def list_teachers(users: CreateUserReuest = Depends(get_list_students)):
    return users


@app.get('/admin/books', status_code=status.HTTP_200_OK, tags=["admin"])
async def list_books(data: CreateUserReuest = Depends(get_book_list)):
    return data


@app.get('/admin/statistics', status_code=status.HTTP_200_OK, tags=["admin"])
async def statistic(data: CreateUserReuest = Depends(teacher_statistic)):
    return data
