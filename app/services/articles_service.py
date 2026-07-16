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
from sqlalchemy import exists
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

        article_slug_exists = self._db.query(
            exists().where(Articles.slug == slug)
        ).scalar()

        if article_slug_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="article with this name already exists",
            )

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

    def get_article(self, current_user_id: int, slug: str):
        article = self._db.query(Articles).filter(Articles.slug == slug).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="article not found"
            )
        params = article.__dict__.copy()
        params.pop("authorId")
        author = article.author
        following = author.id != current_user_id and any(
            follower.follower_id == current_user_id for follower in author.followers
        )
        params.update(
            {
                "author": ProfileModel(
                    username=author.username,
                    bio=author.bio,
                    image=author.image,
                    following=following,
                )
            }
        )

        return ArticleModelResponse(article=ArticleModelResponseInner(**params))

    def delete_article(self, current_user_id: int, slug: str):
        article = (
            self._db.query(Articles)
            .filter(
                Articles.slug == slug.casefold(), Articles.authorId == current_user_id
            )
            .first()
        )
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="article not found"
            )

        self._db.delete(article)
        self._db.commit()
