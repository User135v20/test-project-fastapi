from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from core.logic import find_user_by_email
from core.security import create_access_token, hash_password, password_verification, check_token
from db.database import get_db
from models import User
from schemas import CreateUserReuest, AuthModel, Token

app = FastAPI()

@app.post("/auth")
def create(detail: CreateUserReuest, db: Session = Depends(get_db)):
    if find_user_by_email(detail.email, db) is not None:
        return 'user with this  email already exists'
    try:
        to_create = User(
            full_name=detail.full_name,
            email=detail.email,
            password=hash_password(detail.password),
            role=detail.role,
            is_superuser=detail.is_superuser
        )
        db.add(to_create)
        db.commit()
        return {
            "success": True,
            "id": to_create.id}
    except:
        return 'Failed to signup user'


@app.get("/get")
def get_by_id(id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == id).first()


@app.post('/login')
def login(detail: AuthModel, db: Session = Depends(get_db)):
    try:
        user_by_email = find_user_by_email(detail.email, db)
        if user_by_email is None:
            raise
        if not password_verification(detail.password, user_by_email.password):
            return HTTPException(status_code=401, detail='Invalid password')
        access_token = create_access_token({"role": user_by_email.role, "email": user_by_email.email})
        return {'access_token': access_token, "token_type": "bearer",}
    except:
        return HTTPException(status_code=401, detail='Invalid email')

@app.post('/check_token')
def check_tokens(detail: Token):
    a = check_token(detail.access_token)
    return {'check token': a}
