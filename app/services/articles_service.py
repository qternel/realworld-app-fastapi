from datetime import datetime
from typing import Annotated

from db.db_models import Articles, Users
from db.utils import get_db
from fastapi import Depends, HTTPException
from models.articles_models import (
    ArticleModelResponse,
    ArticleModelResponseInner,
    CreateArticleModel,
)
from models.profiles_models import ProfileModel
from sqlalchemy.orm import Session
from starlette import status


class ArticlesService:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self._db = db

    def create_article(self, current_user_id: int, article_request: CreateArticleModel):
        usr = self._db.query(Users).filter(Users.id == current_user_id).first()
        if usr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )
        slug = "-".join(article_request.article.title.lower().split())
        created_at = datetime.now()
        article = Articles(
            slug=slug,
            title=article_request.article.title,
            description=article_request.article.description,
            body=article_request.article.body,
            tagList=article_request.article.tagList,
            createdAt=created_at,
            updatedAt=created_at,
            authorId=current_user_id,
        )
        self._db.add(article)
        self._db.commit()
        return ArticleModelResponse(
            article=ArticleModelResponseInner(
                slug=slug,
                title=article_request.article.title,
                description=article_request.article.description,
                body=article_request.article.body,
                tagList=article_request.article.tagList,
                createdAt=created_at,
                updatedAt=created_at,
                author=ProfileModel(
                    username=usr.username, bio=usr.bio, image=usr.image, following=False
                ),
            )
        )
