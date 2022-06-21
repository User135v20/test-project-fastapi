from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.by_token import to_book, list_of_classes_for_a_student, cancel_a_booked_lesson, find_free_teachers
from core.logic import add_users, find_user_and_role_by_email
from core.security import password_verification, create_access_token, check_token
from db.database import get_db
from schemas import CreateUserReuest, Token

app = FastAPI()


@app.post("/auth")
def create(detail: CreateUserReuest, db: Session = Depends(get_db)):
    return add_users(detail, db)


@app.post('/token', response_model=Token)
def login(db: Session = Depends(get_db), detail: OAuth2PasswordRequestForm = Depends()):
    try:
        user_and_role_by_email = find_user_and_role_by_email(detail.username, db)
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


@app.post('/check_token')
def check_user_token(detail: str):
    return check_token(detail)


@app.post('/student/to_book')
def make_an_appointments(user: CreateUserReuest = Depends(to_book)):
    return user


@app.post('/student/list_of_classes')
def list_of_classes(user: CreateUserReuest = Depends(list_of_classes_for_a_student)):
    return user

@app.post('/student/cancel_lesson')
def cancel_lesson(user: CreateUserReuest = Depends(cancel_a_booked_lesson)):
    return user


@app.post('/student/free_teacher')
def list_of_available_teachers(list_teachers: CreateUserReuest = Depends(find_free_teachers)):
    return list_teachers


