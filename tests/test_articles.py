import httpx
from fastapi.testclient import TestClient
from starlette import status

from app.main import app
from tests.test_profiles import user1, user2

test_client = TestClient(app)


def test_create_article():
    response: httpx.Response = test_client.post(
        "/api/articles",
        headers={"Authorization": f"Token {user1.get("token")}"},
        json={
            "article": {
                "title": "cool title",
                "description": "description",
                "body": "body",
                "tagList": ["tag1", "tag2", "tag3", "tag4"],
            }
        },
    )
    assert response.status_code == status.HTTP_201_CREATED

    response_json_inner = response.json().get("article")
    assert response_json_inner is not None

    assert response_json_inner.get("slug") == "cool-title"
    assert response_json_inner.get("favorited") == False
    assert response_json_inner.get("favoritesCount") == 0
    author = response_json_inner.get("author")

    assert author.get("username") == user1.get("username")
    assert author.get("bio") == user1.get("bio")
    assert author.get("image") == user1.get("image")
    assert author.get("following") == False


def test_create_article_fail():
    pass


def test_feed_articles():
    pass


def test_feed_articles_fail():
    pass


def test_get_article():
    pass


def test_get_article_fail():
    pass


def test_update_article():
    pass


def test_update_article_fail():
    pass


def test_delete_article():
    pass


def test_delete_article_fail():
    pass


def test_favorite_article():
    pass


def test_favorite_article_fail():
    pass


def test_unfavorite_article():
    pass


def test_unfavorite_article_fail():
    pass


def test_get_tags():
    response: httpx.Response = test_client.get("/api/tags")

    assert response.status_code == status.HTTP_200_OK
    tags = response.json().get("tags")
    assert "tag1" in tags
    assert "tag2" in tags
    assert "tag3" in tags
    assert "tag4" in tags


def test_add_comment():
    pass


def test_add_comment_fail():
    pass


def test_delete_comment():
    pass


def test_delete_comment_fail():
    pass


def test_get_comments():
    pass


def test_get_comments_fail():
    pass


def test_list_articles():
    pass


def test_list_articles_fail():
    pass
