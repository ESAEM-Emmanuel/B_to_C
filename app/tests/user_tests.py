from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_access_token():
    data = {"user_id": "123"}
    token = create_access_token(data)
    assert isinstance(token, str)