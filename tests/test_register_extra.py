import pytest
from fastapi.testclient import TestClient
from user_service.main import app

client = TestClient(app)

def test_register_success():
    user = {"username": "testuser", "email": "testuser@example.com", "password": "StrongPass1!"}
    response = client.post("/register", json=user)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_register_duplicate_email():
    user = {"username": "dupe", "email": "dupe@example.com", "password": "StrongPass1!"}
    client.post("/register", json=user)
    response = client.post("/register", json=user)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_register_weak_password():
    user = {"username": "weak", "email": "weak@example.com", "password": "12345678"}
    response = client.post("/register", json=user)
    assert response.status_code == 422

def test_register_missing_fields():
    user = {"username": "", "email": "", "password": ""}
    response = client.post("/register", json=user)
    assert response.status_code == 422

def test_session_check():
    user = {"username": "session", "email": "session@example.com", "password": "StrongPass1!"}
    reg = client.post("/register", json=user)
    token = reg.json()["access_token"]
    response = client.get("/session", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Session is valid"

def test_session_invalid_token():
    response = client.get("/session", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Session expired or token invalid"
