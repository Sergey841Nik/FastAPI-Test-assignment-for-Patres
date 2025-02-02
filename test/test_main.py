# Я понимаю, что сделал слишком мало тестов. Но признаюсь честно, что я не успел разобраться более глубоко в юнит-тестах.
# Впредь обещаю исправляться.

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Это стартовое сообщение"}

@pytest.mark.asyncio
async def test_register_users():
    response = client.post(
        "/auth/register/",
        json={
            "email": "user@example.com",
            "first_name": "string",
            "last_name": "string",
            "password": "string",
            "confirm_password": "string"
            },
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "Пользователь уже существует"}   

@pytest.mark.asyncio
async def test_auth_user():
    response = client.post(
        "/auth/login/",
        json={"email": "admin@example.com", "password": "qwerty"},
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_take_book():
    response = client.post(
        "/api_library/take_book/3/1",
    )
    assert response.status_code == 200
    
