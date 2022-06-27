from typing import Optional

from pydantic import BaseModel, EmailStr


class UserFromCsv(BaseModel):
    last_name: Optional[str]
    first_name: Optional[str]
    fatherland: Optional[str]
    language: Optional[str] = None


class CreateUserReuest(BaseModel):
    full_name: str
    email: Optional[EmailStr]
    password: Optional[str]
    role: Optional[str]
    language: Optional[str] = None


class AuthModel(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
