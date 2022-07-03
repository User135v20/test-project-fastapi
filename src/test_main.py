import re

from fastapi.testclient import TestClient

from core.security import create_access_token
from main import app

#
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:rty56rty56@localhost:5432/postgres"
#
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )
# TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#
#
# Base.metadata.create_all(bind=engine)
#
#
# def override_get_db():
#     try:
#         db = TestingSessionLocal()
#         yield db
#     finally:
#         db.close()
#
#
# app.dependency_overrides[get_db] = override_get_db
# db_conn = override_get_db

client = TestClient(app)
STUDENT_NAME = "Full_Name Student5"
STUDENT_EMAIL = "test_student5@test.com"
STUDENT_PASSWORD = "PasswordPas1"
STUDENT_ROLE = "student"
TEACHER_NAME = "Швец Родион Муратович"
TEACHER_EMAIL = "test_teacher@test.com"
TEACHER_PASSWORD = "PasswordPas1"
TEACHER_ROLE = "teacher"
TEACHER_LANGUAGE = "English"
FROM_DATE = "1000-12-12"
DATE_LESSON = "2000-12-12"
TO_DATE = "3000-12-12"
AUTH_ERROR = '{"detail":"user does not have access rights"}'


# def test_add_from_csv():
#     response = client.post("/add_teacher_from_csv")
#     assert response.status_code == 201
#     assert "success" in response.text


class BaseApi:
    url = 'http://127.0.0.1:8000'
    auth_url = f"{url}/auth"
    student_delete_url = f"{url}/delete_user/student?id_user="
    student_to_book = f"{url}/student/to_book?date="
    student_classes = f"{url}/student/list_of_classes?from_date="
    student_cancel_lesson_url = f"{url}/student/cancel_lesson?date="
    teacher_classes_url = f"{url}/teacher/list_of_classes?from_date="
    teacher_add_lang_url = f"{url}/teacher/add_language?language="
    teacher_remove_lang_url = f"{url}/teacher/remove_language?language="
    teacher_cancel_lesson_url = f"{url}/teacher/cancel_lesson?date="


class TestTeacher(BaseApi):
    response = client.post('http://127.0.0.1:8000/auth', json={
        "full_name": STUDENT_NAME,
        "email": STUDENT_EMAIL,
        "password": STUDENT_PASSWORD,
        "role": STUDENT_ROLE,
        "language": ""
    })
    student_id = re.findall('\d+', response.text)[0]
    token_for_user = create_access_token({"role": "student", "email": STUDENT_EMAIL})

    response = client.post('http://127.0.0.1:8000/auth', json={
        "full_name": TEACHER_NAME,
        "email": TEACHER_EMAIL,
        "password": TEACHER_PASSWORD,
        "role": TEACHER_ROLE,
        "language": TEACHER_LANGUAGE
    })

    # def setup(self):
    #     response = client.post(self.auth_url, json={
    #         "full_name": STUDENT_NAME,
    #         "email": STUDENT_EMAIL,
    #         "password": STUDENT_PASSWORD,
    #         "role": STUDENT_ROLE,
    #         "language": ""
    #     })
    #     assert response.status_code == 201
    #     self.student_id = re.findall('\d+', response.text)[0]
    #     self.token_for_user = create_access_token({"role": "student", "email": STUDENT_EMAIL})

    def test_list_teachers_classes(self):
        response = client.get(
            f'{self.teacher_classes_url}{FROM_DATE}&to_date={TO_DATE}',
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.token_for_user}",
            }
        )
        assert response.status_code == 401
        assert response.text == f"{AUTH_ERROR}"

    def test_add_languages(self):
        response = client.post(
            f"{self.teacher_add_lang_url}{TEACHER_LANGUAGE}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.token_for_user}",
            }
        )
        assert response.status_code == 401
        assert response.text == f'{AUTH_ERROR}'

    def test_remove_languages(self):
        response = client.delete(
            f"{self.teacher_remove_lang_url}{TEACHER_LANGUAGE}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.token_for_user}",
            })
        assert response.status_code == 401
        assert response.text == f'{AUTH_ERROR}'

    def test_cancel_lesson_for_teacher(self):
        response = client.delete(
            f"{self.teacher_cancel_lesson_url}{FROM_DATE}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.token_for_user}",
            })
        assert response.status_code == 401
        assert response.text == f'{AUTH_ERROR}'

    def test_make_an_appointments(self):
        response = client.post(
            f"{self.student_to_book}{DATE_LESSON}&teacher_name={TEACHER_NAME}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.token_for_user}",
            })
        assert response.status_code == 201

    def test_list_students_classes(self):
        response = client.get(
            f"{self.student_classes}{FROM_DATE}&to_date={TO_DATE}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.token_for_user}",
            }
        )
        assert response.status_code == 200
        assert response.text == f'["{DATE_LESSON}  {TEACHER_NAME}"]'

    def test_cancel_lesson_for_student(self):
        response = client.delete(
            f"{self.student_cancel_lesson_url}{DATE_LESSON}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.token_for_user}",
            })
        assert response.status_code == 200
        assert response.text == f'"{DATE_LESSON} is free"'

    def test_list_students_classes_after_cancel(self):
        response = client.get(
            f"{self.student_classes}{FROM_DATE}&to_date{DATE_LESSON}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {self.token_for_user}",
            }
        )
        assert response.status_code == 200
        assert response.text == '"this date is free or these dates are free"'


    # def teardown(self):
    #             client.delete(f"{self.url}/delete_user/student/{self.student_id}")
    # client.delete(f"{self.student_delete_url}{self.student_id}")
    # assert response_teardown.status_code == 200

# ------------------------------------------------------------------------------
# def test_create_users():
#     response = client.post(
#         "/auth",
#         json={
#             "full_name": STUDENT_NAME,
#             "email": STUDENT_EMAIL,
#             "password": STUDENT_PASSWORD,
#             "role": STUDENT_ROLE,
#             "language": ""}
#     )
#     assert response.status_code == 201
#     assert "success" in response.text
#
#
# # def test_delete_student_user():
# #     id_user = re.findall('\d+', response.text)
# #     client.delete(
# #         f"/delete_user/student?id_user={id_user}"
# #     )
#
#
# def test_login():
#     response = client.post(
#         "/token",
#         {"username": STUDENT_EMAIL,
#          "password": STUDENT_PASSWORD},
#     )
#     assert response.status_code == 200
#
#
# def test_list_teachers_classes():
#     token_for_user = create_access_token({"role": "student", "email": "email@mail.com"})
#     response = client.get(
#         'http://127.0.0.1:8000/teacher/list_of_classes?from_date=2012-12-12&to_date=2012-12-12',
#         headers={
#             "accept": "application/json",
#             "Authorization": f"Bearer {token_for_user}",
#         }
#     )
#     assert response.status_code == 401
#     assert response.text == '{"detail":"user does not have access rights"}'
