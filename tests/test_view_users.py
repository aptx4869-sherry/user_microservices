import pytest
from fastapi.testclient import TestClient
from user_service.main import app

client = TestClient(app)

def test_brewboard_no_users():
    response = client.get("/brewboard")
    assert response.status_code == 404
    assert response.json()["detail"].startswith("No brewers")

def test_brewboard_with_users():
    user = {"username": "brew", "email": "brew@example.com", "password": "StrongPass1!"}
    client.post("/register", json=user)
    response = client.get("/brewboard")
    assert response.status_code == 200
    assert any(u["email"] == "brew@example.com" for u in response.json())
