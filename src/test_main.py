from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_add_from_csv():
    response = client.post("/add_teacher_from_csv")
    assert response.status_code == 201
    assert "success" in response.text
