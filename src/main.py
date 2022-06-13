from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from models import User, AuthModel
from schemas import CreateUserReuest
from database import get_db

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/auth")
def create(detail: CreateUserReuest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == detail.email).first() != None:
        return 'user with this  email already exists'
    try:
        to_create = User(
            full_name=detail.full_name,
            email=detail.email,
            password=pwd_context.hash(detail.password),
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
        user_by_email = db.query(User).filter(User.email == detail.email).first()
        if (user_by_email is None):
            raise
        if not pwd_context.verify(detail.password, user_by_email.password):
            return HTTPException(status_code=401, detail='Invalid password')
        access_token = "auth_handler.encode_token(user_by_email['key'])"
        # access_token = auth_handler.encode_token(user_by_email['key'])
        # refresh_token = auth_handler.encode_refresh_token(user_by_email['key'])
        refresh_token = "auth_handler.encode_refresh_token(user_by_email['key'])"
        return {'access_token': access_token, 'refresh_token': refresh_token}
    except:
        return HTTPException(status_code=401, detail='Invalid email')


