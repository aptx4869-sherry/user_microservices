import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests
import pytest
from Read_properties import get_registration_data

@pytest.fixture
def user_data():
    data = get_registration_data()
    return {
        "username": data["username"],
        "email": data["email"],
        "password": data["password"],
    }

@pytest.fixture
def register_url():
    return get_registration_data()["url"]



def test_user_registration(user_data):
    from Read_properties import get_registration_data
    url = get_registration_data()["url"]
    response = requests.post(url, json=user_data)
    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"
    print(f"Registration response: {response_data}")


def test_duplicate_email(user_data):
    from Read_properties import get_registration_data
    url = get_registration_data()["url"]
    # Register first time
    requests.post(url, json=user_data)
    # Register again with same email
    response = requests.post(url, json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


def test_invalid_email():
    from Read_properties import get_registration_data
    url = get_registration_data()["url"]
    payload = {
        "username": "user2",
        "email": "not-an-email",
        "password": "pass"
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 422
    print(f"Invalid email response: {response.json()}")


def test_missing_fields():
    from Read_properties import get_registration_data
    url = get_registration_data()["url"]
    payload = {
        "username": "user3"
        # missing email and password
    }
    response = requests.post(url, json=payload)
    assert response.status_code == 422
    response_data = response.json()
    assert "detail" in response_data
    # Check that the error mentions missing fields
    error_msgs = [err["msg"] for err in response_data["detail"]]
    assert any("field required" in msg for msg in error_msgs)
    print(f"Missing fields response: {response_data}")
