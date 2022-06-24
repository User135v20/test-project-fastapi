from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.for_admin import get_list_teachers, get_list_students, get_book_list, teacher_statistic
from core.for_students import to_book, list_of_classes_for_student, find_free_teachers, cancel_a_booked_lesson_student
from core.for_teachers import list_of_classes_for_teacher, add_language, cancel_a_booked_lesson_teacher, remove_language
from core.logic import add_users, find_user_by_email
from core.security import password_verification, create_access_token
from db.database import get_db
from schemas import CreateUserReuest, Token

app = FastAPI()


@app.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_users(detail: CreateUserReuest, db: Session = Depends(get_db)):
    return add_users(detail, db)


@app.post('/token', response_model=Token)
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


@app.post('/student/to_book', status_code=status.HTTP_201_CREATED)
async def make_an_appointments(user: CreateUserReuest = Depends(to_book)):
    return user


@app.get('/student/list_of_classes')
async def list_of_classes(user: CreateUserReuest = Depends(list_of_classes_for_student)):
    return user


@app.delete('/student/cancel_lesson')
async def cancel_lesson(user: CreateUserReuest = Depends(cancel_a_booked_lesson_student)):
    return user


@app.get('/student/free_teacher')
async def list_of_available_teachers(list_classes: CreateUserReuest = Depends(find_free_teachers)):
    return list_classes


@app.get('/teacher/list_of_classes')
async def list_of_available_teachers(list_classes: CreateUserReuest = Depends(list_of_classes_for_teacher)):
    return list_classes


@app.post('/teacher/add_language', status_code=status.HTTP_201_CREATED)
async def add_languages(result: CreateUserReuest = Depends(add_language)):
    return result


@app.delete('/teacher/remove_language')
async def remove_languages(result: CreateUserReuest = Depends(remove_language)):
    return result


@app.delete('/teacher/cancel_lesson')
async def cancel_lesson(result: CreateUserReuest = Depends(cancel_a_booked_lesson_teacher)):
    return result


@app.get('/admin/list_teachers')
async def list_teachers(users: CreateUserReuest = Depends(get_list_teachers)):
    return users


@app.get('/admin/list_students')
async def list_teachers(users: CreateUserReuest = Depends(get_list_students)):
    return users


@app.get('/admin/books')
async def list_teachers(data: CreateUserReuest = Depends(get_book_list)):
    return data


@app.get('/admin/statistics')
async def statistic(data: CreateUserReuest = Depends(teacher_statistic)):
    return data
