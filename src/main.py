from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.for_admin import get_list_teachers, get_list_students, get_book_list, teacher_statistic
from core.for_students import to_book, list_of_classes_for_student, find_free_teachers, cancel_a_booked_lesson_student
from core.for_teachers import list_of_classes_for_teacher, add_language, cancel_a_booked_lesson_teacher, remove_language
from core.logic import add_users, find_user_by_email, read_from_csv, create_teacher, check_by_name, find_by_name, \
    get_language_id, check_skills, add_skill, add_language_to_db
from core.security import password_verification, create_access_token
from db.database import get_db
from models import Teacher
from schemas import CreateUserReuest, Token

FILE_NAME = "user.csv"
app = FastAPI()


@app.post("/add_csv", status_code=status.HTTP_201_CREATED)
def add_from_csv(db: Session = Depends(get_db)):
    count_added = 0
    count_updated = 0
    list_result_parse = read_from_csv(FILE_NAME)
    for el in list_result_parse:
        full_name = str(el.last_name) + " " + str(el.first_name) + " " + str(el.fatherland)
        if len(el.language) < 1:
            language = None
        else:
            language = el.language
        user = CreateUserReuest(
            full_name=full_name,
            language=language)
        if check_by_name(user.full_name, Teacher, db):
            if not check_skills(user, db):
                teacher_id = find_by_name(user.full_name, Teacher, db).id
                language_id = get_language_id(user.language, db)
                if language_id is None:
                    language_id = add_language_to_db(language, db)
                add_skill(db, teacher_id, language_id)
                count_updated += 1

        else:
            create_teacher(user, db)
            count_added += 1
    return {"success": True,
            "number of added teachers": count_added,
            "number of updated teachers": count_updated}


@app.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_users(detail: CreateUserReuest, db: Session = Depends(get_db)):
    return add_users(detail, db)


@app.post('/token', response_model=Token, status_code=status.HTTP_201_CREATED)
async def login(db: Session = Depends(get_db), detail: OAuth2PasswordRequestForm = Depends()):
    try:
        user_and_role_by_email = find_user_by_email(detail.username, db, return_role=True)
        if user_and_role_by_email is None:
            raise
        user = user_and_role_by_email[0]
        user_role = user_and_role_by_email[1]
        if not password_verification(detail.password, user.password):
            return HTTPException(status_code=401, detail='Invalid password')
        access_token = create_access_token({"role": user_role, "email": user.email})
        return {'access_token': access_token, "token_type": "bearer", }
    except:
        return HTTPException(status_code=401, detail='Invalid email')


@app.post('/student/to_book', status_code=status.HTTP_201_CREATED, tags=["student"])
async def make_an_appointments(user: CreateUserReuest = Depends(to_book)):
    return user


@app.get('/student/list_of_classes', status_code=status.HTTP_200_OK, tags=["student"])
async def list_of_classes(user: CreateUserReuest = Depends(list_of_classes_for_student)):
    return user


@app.delete('/student/cancel_lesson', status_code=status.HTTP_200_OK, tags=["student"])
async def cancel_lesson(user: CreateUserReuest = Depends(cancel_a_booked_lesson_student)):
    return user


@app.get('/student/free_teacher', status_code=status.HTTP_200_OK, tags=["student"])
async def list_of_available_teachers(list_classes: CreateUserReuest = Depends(find_free_teachers)):
    return list_classes


@app.get('/teacher/list_of_classes', status_code=status.HTTP_200_OK, tags=["teacher"])
async def list_of_available_teachers(list_classes: CreateUserReuest = Depends(list_of_classes_for_teacher)):
    return list_classes


@app.post('/teacher/add_language', status_code=status.HTTP_201_CREATED, tags=["teacher"])
async def add_languages(result: CreateUserReuest = Depends(add_language)):
    return result


@app.delete('/teacher/remove_language', status_code=status.HTTP_200_OK, tags=["teacher"])
async def remove_languages(result: CreateUserReuest = Depends(remove_language)):
    return result


@app.delete('/teacher/cancel_lesson', status_code=status.HTTP_200_OK, tags=["teacher"])
async def cancel_lesson(result: CreateUserReuest = Depends(cancel_a_booked_lesson_teacher)):
    return result


@app.get('/admin/list_teachers', status_code=status.HTTP_200_OK, tags=["admin"])
async def list_teachers(users: CreateUserReuest = Depends(get_list_teachers)):
    return users


@app.get('/admin/list_students', status_code=status.HTTP_200_OK, tags=["admin"])
async def list_teachers(users: CreateUserReuest = Depends(get_list_students)):
    return users


@app.get('/admin/books', status_code=status.HTTP_200_OK, tags=["admin"])
async def list_books(data: CreateUserReuest = Depends(get_book_list)):
    return data


@app.get('/admin/statistics', status_code=status.HTTP_200_OK, tags=["admin"])
async def statistic(data: CreateUserReuest = Depends(teacher_statistic)):
    return data
