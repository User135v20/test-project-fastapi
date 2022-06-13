from typing import Optional

from pydantic import BaseModel, EmailStr


class CreateUserReuest(BaseModel):
    full_name: str
    email: Optional[EmailStr]
    password: str
    role: str
    is_superuser: bool
