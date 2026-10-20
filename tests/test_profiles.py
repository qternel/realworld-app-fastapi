import httpx
from fastapi.testclient import TestClient
from starlette import status

from app.main import app
from tests.test_auth import email, password, username
from tests.test_user import bio, image

test_client = TestClient(app)


user1 = (
    test_client.post(
        "/api/users/login", json={"user": {"email": email, "password": password}}
    )
    .json()
    .get("user")
)


username2 = "test"
password2 = "test"
email2 = "test@test.com"

user2 = (
    test_client.post(
        "/api/users",
        json={
            "user": {
                "username": username2,
                "password": password2,
                "email": email2,
            }
        },
    )
    .json()
    .get("user")
)

user1_token = user1.get("token")


def test_get_profile():
    response: httpx.Response = (
        test_client.get(f"api/profiles/{username}").json().get("profile")
    )
    assert response.get("username") == username
    assert response.get("bio") == bio
    assert response.get("image") == image
    assert response.get("following") == False


def test_get_profile_fail():
    response: httpx.Response = test_client.get("api/profiles/this_user_does_not_exist")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_follow_user():
    response: httpx.Response = (
        test_client.post(
            f"/api/profiles/{username2}/follow",
            headers={"Authorization": f"Token {user1_token}"},
        )
        .json()
        .get("profile")
    )

    # print(user2)
    print(response)

    assert response.get("username") == username2
    assert response.get("following") == True

    response: httpx.Response = (
        test_client.get(
            f"api/profiles/{username2}",
            headers={"Authorization": f"Token {user1_token}"},
        )
        .json()
        .get("profile")
    )
    assert response.get("following") == True


def test_follow_user_fail():
    response: httpx.Response = test_client.post(
        "/api/profiles/this_user_does_not_exist/follow",
        headers={"Authorization": f"Token {user1_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response: httpx.Response = test_client.post(
        f"/api/profiles/{username}/follow",
        headers={"Authorization": f"Token {user1_token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_unfollow_user():
    response: httpx.Response = (
        test_client.delete(
            f"/api/profiles/{username2}/follow",
            headers={"Authorization": f"Token {user1_token}"},
        )
        .json()
        .get("profile")
    )
    assert response.get("following") == False

    response: httpx.Response = (
        test_client.get(
            f"api/profiles/{username2}",
            headers={"Authorization": f"Token {user1_token}"},
        )
        .json()
        .get("profile")
    )
    assert response.get("following") == False


def test_unfollow_user_fail():
    user1_token = user1.get("token")
    response: httpx.Response = test_client.delete(
        "/api/profiles/this_user_does_not_exist/follow",
        headers={"Authorization": f"Token {user1_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
