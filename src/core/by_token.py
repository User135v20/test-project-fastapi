from datetime import date

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from core.logic import find_user_by_email
from core.security import SECRET_KEY, ALGORITHM
from db.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")



async def find_user_by_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
    role = payload.get("role")
    email = payload.get("email")
    return find_user_by_email(email, db, role)
