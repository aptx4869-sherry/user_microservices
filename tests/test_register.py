import pytest
from fastapi.testclient import TestClient
from user_service.main import app

client = TestClient(app)

test_cases = [
    ({"username": "alice", "email": "alice@example.com", "password": "secret123"}, 200),
    ({"username": "bob", "email": "invalid-email", "password": "pass"}, 422),
    ({"username": "", "email": "test@example.com", "password": "123456"}, 422),
    ({"username": "alice", "email": "alice@example.com", "password": "anotherpass"}, 400),  # duplicate email
    ({"username": "alice", "email": "abcd@example.com", "password": "password123"}, 400)
]

@pytest.mark.parametrize("user_input,expected_status", test_cases)
def test_register_cases(user_input, expected_status):
    response = client.post("/register", json=user_input)
    if response.status_code != expected_status:
        print(f"\n❌ Failed Test Case:\nInput: {user_input}\nExpected: {expected_status}, Got: {response.status_code}\nResponse: {response.json()}")
    else:
        print(f"\n✅ Passed Test Case: {user_input}")
    assert response.status_code == expected_status
