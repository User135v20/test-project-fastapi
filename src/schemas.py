from pydantic import BaseModel


class CreateUserReuest(BaseModel):
    full_name: str
    email: str
    password: str
    is_teacher: bool
