from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from models import User
from schemas import CreateUserReuest
from database import get_db

app = FastAPI()


@app.post("/")
def create(detail: CreateUserReuest, db: Session = Depends(get_db)):
    to_create = User(
        full_name=detail.full_name,
        email=detail.email,
        password=detail.password,
        is_teacher=detail.is_teacher
    )
    db.add(to_create)
    db.commit()
    return {
        "success": True,
        "id": to_create.id
    }


@app.get("/")
def get_by_id(id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == id).first()
