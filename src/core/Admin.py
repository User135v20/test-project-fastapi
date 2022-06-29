from sqlalchemy.orm import Session
from core.Commons import add_into_db
from core.security import hash_password
from models import Admin
from schemas import CreateUserReuest


def create_admin(detail: CreateUserReuest, db_connect: Session):
    user = Admin(
        full_name=detail.full_name,
        email=detail.email,
        password=hash_password(detail.password),
    )
    add_into_db(user, db_connect)
    return user
