import re
from datetime import timedelta, datetime
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def check_password(password):
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$"
    if re.match(pattern, password) is None:
        raise HTTPException(status_code=401, detail="Password has incorrect format")


def hash_password(password: str):
    if password is None:
        return None
    try:
        check_password(password)
        return pwd_context.hash(password)
    except Exception as err:
        raise err


def password_verification(password: str, users_hash_password: str):
    return pwd_context.verify(password, users_hash_password)


def checking_for_access_rights(token, role):
    if role != jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM).get("role"):
        raise HTTPException(status_code=401, detail="user does not have access rights")


def create_access_token(data: dict):
    to_encode = data.copy()
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
