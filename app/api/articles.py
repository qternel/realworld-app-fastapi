from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from models.articles_models import (
    ArticleModelResponse,
    CommentRequest,
    CommentResponse,
    CreateArticleModel,
    UpdateArticleModel,
)
from services.articles_service import ArticlesService
from services.auth_service import check_jwt_optional, check_jwt_required
from starlette import status

router = APIRouter()


@router.post(
    "/api/articles",
    status_code=status.HTTP_201_CREATED,
    response_model=ArticleModelResponse,
)
async def create_article(
    payload: Annotated[dict, Depends(check_jwt_required)],
    article_request: CreateArticleModel,
    articles_service: Annotated[ArticlesService, Depends()],
):
    return articles_service.create_article(int(payload.get("sub")), article_request)


@router.get(
    "/api/articles/{slug}",
    status_code=status.HTTP_200_OK,
    response_model=ArticleModelResponse,
)
async def get_article(
    payload: Annotated[dict, Depends(check_jwt_optional)],
    slug: Annotated[str, Path(min_length=1)],
    articles_service: Annotated[ArticlesService, Depends()],
):
    return articles_service.get_article(int(payload.get("sub")), slug)


@router.put(
    "/api/articles/{slug}",
    status_code=status.HTTP_200_OK,
    response_model=ArticleModelResponse,
)
async def update_article(
    payload: Annotated[dict, Depends(check_jwt_required)],
    slug: Annotated[str, Path(min_length=1)],
    update_request: UpdateArticleModel,
    articles_service: Annotated[ArticlesService, Depends()],
):
    return articles_service.update_article(
        int(payload.get("sub")), slug, update_request
    )


@router.delete("/api/articles/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    payload: Annotated[dict, Depends(check_jwt_required)],
    slug: Annotated[str, Path(min_length=1)],
    articles_service: Annotated[ArticlesService, Depends()],
):
    return articles_service.delete_article(int(payload.get("sub")), slug)


@router.post(
    "/api/articles/{slug}/favorite",
    status_code=status.HTTP_200_OK,
    response_model=ArticleModelResponse,
)
async def favorite_article(
    slug: Annotated[str, Path(min_length=1)],
    payload: Annotated[str, Depends(check_jwt_required)],
    articles_service: Annotated[ArticlesService, Depends()],
):
    return articles_service.favorite_article(int(payload.get("sub")), slug)


@router.delete(
    "/api/articles/{slug}/favorite",
    status_code=status.HTTP_200_OK,
    response_model=ArticleModelResponse,
)
async def unfavorite_article(
    slug: Annotated[str, Path(min_length=1)],
    payload: Annotated[str, Depends(check_jwt_required)],
    articles_service: Annotated[ArticlesService, Depends()],
):
    return articles_service.unfavorite_article(int(payload.get("sub")), slug)


@router.get("/api/tags", status_code=status.HTTP_200_OK)
async def get_tags(articles_service: Annotated[ArticlesService, Depends()]):
    return articles_service.get_tags()


@router.post(
    "/api/articles/{slug}/comments",
    status_code=status.HTTP_201_CREATED,
    response_model=CommentResponse,
)
async def add_comment(
    slug: Annotated[str, Path(min_length=1)],
    comment_request: CommentRequest,
    payload: Annotated[dict, Depends(check_jwt_required)],
    articles_service: Annotated[ArticlesService, Depends()],
):
    return articles_service.add_comment(int(payload.get("sub")), slug, comment_request)


@router.delete(
    "/api/articles/{slug}/comments/{id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_comment(
    slug: Annotated[str, Path(min_length=1)],
    id: Annotated[int, Path(ge=1)],
    payload: Annotated[dict, Depends(check_jwt_required)],
    articles_service: Annotated[ArticlesService, Depends()],
):
    return articles_service.delete_comment(slug, id)
