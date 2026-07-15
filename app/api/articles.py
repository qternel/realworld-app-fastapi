from typing import Annotated

from fastapi import APIRouter, Depends
from models.articles_models import ArticleModelResponse, CreateArticleModel
from services.articles_service import ArticlesService
from services.auth_service import check_jwt_required
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
