import httpx
from fastapi.testclient import TestClient
from starlette import status

from app.main import app
from app.services.auth_service import AuthService

test_client = TestClient(app)

username = "mike"
password = "mike"
email = "mike@mike.com"


def test_register_user():

    response: httpx.Response = test_client.post(
        "/api/users",
        json={
            "user": {
                "username": username,
                "password": password,
                "email": email,
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    response_json_inner = response.json().get("user")
    assert response_json_inner is not None

    assert response_json_inner.get("email") == email
    assert response_json_inner.get("token") == AuthService.create_jwt_token(
        payload={"sub": "1", "username": username}, expires_in=120
    )
    assert response_json_inner.get("username") == username
    assert response_json_inner.get("bio") is None
    assert response_json_inner.get("image") is None


def test_sign_user_in():
    response: httpx.Response = test_client.post(
        "api/users/login",
        json={
            "user": {
                "email": email,
                "password": password,
            }
        },
    )

    assert response.status_code == status.HTTP_200_OK

    response_json_inner = response.json().get("user")
    assert response_json_inner is not None

    assert response_json_inner.get("email") == email
    assert response_json_inner.get("token") == AuthService.create_jwt_token(
        payload={"sub": "1", "username": username}, expires_in=120
    )
    assert response_json_inner.get("username") == username
    assert response_json_inner.get("bio") is None
    assert response_json_inner.get("image") is None


def test_register_user_fail():

    response: httpx.Response = test_client.post(
        "/api/users",
        json={
            "user": {
                "username": username,
                "password": password,
                "email": "123" + email,
            }
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT

    response: httpx.Response = test_client.post(
        "/api/users",
        json={
            "user": {
                "username": "123" + username,
                "password": password,
                "email": email,
            }
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_sign_user_in_fail():
    response: httpx.Response = test_client.post(
        "api/users/login",
        json={
            "user": {
                "email": "123" + email,
                "password": password,
            }
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response: httpx.Response = test_client.post(
        "api/users/login",
        json={
            "user": {
                "email": email,
                "password": "123" + password,
            }
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
