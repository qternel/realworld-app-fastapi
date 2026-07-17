from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from .profiles_models import ProfileModel


class ArticleModel(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=255)]
    description: Annotated[str, Field(min_length=1)]
    body: Annotated[str, Field(min_length=1)]
    tagList: Annotated[list[str] | None, Field(default=None)]


class CreateArticleModel(BaseModel):
    article: ArticleModel


class ArticleModelResponseInner(ArticleModel):
    slug: str
    createdAt: datetime
    updatedAt: datetime
    favorited: bool = False
    favoritesCount: Annotated[int, Field(ge=0)] = 0
    author: ProfileModel


class ArticleModelResponse(BaseModel):
    article: ArticleModelResponseInner


class UpdateArticleModelInner(BaseModel):
    title: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    description: Annotated[str | None, Field(min_length=1)] = None
    body: Annotated[str | None, Field(min_length=1)] = None


class UpdateArticleModel(BaseModel):
    article: UpdateArticleModelInner
