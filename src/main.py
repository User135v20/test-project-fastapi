from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from core.logic import find_user_by_email, add_users
from core.security import create_access_token, password_verification, check_token
from db.database import get_db
from schemas import CreateUserReuest, AuthModel, Token

app = FastAPI()


@app.post("/auth")
def create(detail: CreateUserReuest, db: Session = Depends(get_db)):
    return add_users(detail, db)


@app.post('/login')
def login(detail: AuthModel, db: Session = Depends(get_db)):
    try:
        user_by_email = find_user_by_email(detail.email, db)
        if user_by_email is None:
            raise
        user = user_by_email[0]
        user_role = user_by_email[1]
        if not password_verification(detail.password, user.password):
            return HTTPException(status_code=401, detail='Invalid password')
        access_token = create_access_token({"role": user_role, "email": user.email})
        return {'access_token': access_token, "token_type": "bearer", }
    except:
        return HTTPException(status_code=401, detail='Invalid email')


@app.post('/check_token')
def check_user_token(detail: str):
    return check_token(detail)
