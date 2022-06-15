from fastapi import Depends
from sqlalchemy.orm import Session
from jose import jwt
from models import User


def find_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


