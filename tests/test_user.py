import httpx
from fastapi.testclient import TestClient
from starlette import status

from app.main import app
from tests.test_auth import email, password, username

test_client = TestClient(app)

token = (
    test_client.post(
        "/api/users/login", json={"user": {"email": email, "password": password}}
    )
    .json()
    .get("user")
    .get("token")
)


def test_get_current_user():
    response: httpx.Response = test_client.get(
        "/api/user", headers={"Authorization": f"token {token}"}
    )
    assert response.status_code == status.HTTP_200_OK

    response_json_inner = response.json().get("user")
    assert response_json_inner is not None

    assert response_json_inner.get("email") == email
    assert response_json_inner.get("token") == token
    assert response_json_inner.get("username") == username
    assert response_json_inner.get("bio") is None
    assert response_json_inner.get("image") is None


def test_get_current_user_fail():

    response: httpx.Response = test_client.get(
        "/api/user", headers={"Authorization": f"{token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response: httpx.Response = test_client.get(
        "/api/user", headers={"Authorization": f"token {token}123"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_user():
    response: httpx.Response = test_client.put(
        "/api/user",
        headers={"Authorization": f"Token {token}"},
        json={
            "user": {
                # "email": ...,
                # "username": ...,
                "image": "im.im/im",
                "bio": "cool bio",
            }
        },
    )

    response_json_inner = response.json().get("user")
    assert response_json_inner is not None

    response: httpx.Response = test_client.get(
        "/api/user", headers={"Authorization": f"token {token}"}
    )

    response_json_inner = response.json().get("user")
    assert response_json_inner.get("image") == "im.im/im"
    assert response_json_inner.get("bio") == "cool bio"


def test_update_user_fail():
    response: httpx.Response = test_client.put(
        "/api/user",
        headers={"Authorization": f"Token {token}"},
        json={
            "user": {
                "email": email,
            }
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response: httpx.Response = test_client.put(
        "/api/user",
        headers={"Authorization": f"Token {token}"},
        json={"user": {"username": username}},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
