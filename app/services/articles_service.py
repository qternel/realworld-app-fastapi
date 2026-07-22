from datetime import datetime
from typing import Annotated

from db.db_models import Article, Comment, Tag, User
from db.utils import get_db
from fastapi import Depends, HTTPException
from models.articles_models import (
    ArticleModelResponse,
    ArticleModelResponseInner,
    CommentRequest,
    CommentResponse,
    CommentResponseInner,
    CreateArticleModel,
    UpdateArticleModel,
)
from models.profiles_models import ProfileModel
from sqlalchemy import exists
from sqlalchemy.orm import Session
from starlette import status


class ArticlesService:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self._db = db

    def _get_article_response(self, article: Article, current_user_id: int):
        params = article.__dict__.copy()
        params.pop("authorId")
        params.update(
            {
                "favorited": article
                in self._db.query(User)
                .filter(User.id == current_user_id)
                .first()
                .favorite_articles
            }
        )
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

    def create_article(self, current_user_id: int, article_request: CreateArticleModel):
        usr = self._db.query(User).filter(User.id == current_user_id).first()
        if usr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )
        slug = "-".join(article_request.article.title.lower().split())

        article_slug_exists = self._db.query(
            exists().where(Article.slug == slug)
        ).scalar()

        if article_slug_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="article with this title already exists",
            )

        for t in article_request.article.tagList:
            tag = Tag(name=t)

            if not self._db.query(exists().where(Tag.name == t)).scalar():
                self._db.add(tag)
                self._db.commit()

        created_at = datetime.now()
        article = Article(
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
        self._db.refresh(article)

        return self._get_article_response(article, current_user_id)

    def update_article(
        self, current_user_id: int, slug: str, update_request: UpdateArticleModel
    ):
        article = (
            self._db.query(Article).filter(Article.slug == slug.casefold()).first()
        )

        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="article not found"
            )

        usr = self._db.query(User).filter(User.id == current_user_id).first()
        if article.author != usr:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="you're not the owner of this article",
            )

        new_body = update_request.article.body
        new_description = update_request.article.description
        new_title = update_request.article.title

        all_fields_are_null = all(
            [new_body is None, new_description is None, new_title is None]
        )

        if all_fields_are_null:
            return self._get_article_response(article, current_user_id)

        if new_body is not None:
            article.body = new_body

        if new_description is not None:
            article.description = new_description

        if new_title is not None:
            new_slug = "-".join(new_title.lower().split())
            if self._db.query(exists().where(Article.slug == new_slug)).scalar():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="article with this title already exists",
                )

            article.title = new_title
            article.slug = new_slug

        self._db.add(article)
        self._db.commit()
        self._db.refresh(article)

        return self._get_article_response(article, current_user_id)

    def get_article(self, current_user_id: int, slug: str):
        article = self._db.query(Article).filter(Article.slug == slug).first()
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="article not found"
            )
        return self._get_article_response(article, current_user_id)

    def delete_article(self, current_user_id: int, slug: str):
        article = (
            self._db.query(Article)
            .filter(
                Article.slug == slug.casefold(), Article.authorId == current_user_id
            )
            .first()
        )
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="article not found"
            )

        self._db.delete(article)
        self._db.commit()

    def favorite_article(self, current_user_id: int, slug: str):
        usr = self._db.query(User).filter(User.id == current_user_id).first()
        if usr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )

        article = (
            self._db.query(Article).filter(Article.slug == slug.casefold()).first()
        )
        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="article not found"
            )
        if article not in usr.favorite_articles:
            article.favoritesCount += 1
            usr.favorite_articles.append(article)
            self._db.commit()
            self._db.refresh(article)

        return self._get_article_response(article, current_user_id)

    def unfavorite_article(self, current_user_id: int, slug: str):
        usr = self._db.query(User).filter(User.id == current_user_id).first()
        if usr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )

        article = (
            self._db.query(Article).filter(Article.slug == slug.casefold()).first()
        )
        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="article not found"
            )
        if article in usr.favorite_articles:
            article.favoritesCount -= 1
            usr.favorite_articles.remove(article)
            self._db.commit()
            self._db.refresh(article)

        return self._get_article_response(article, current_user_id)

    def get_tags(self):
        return {"tags": [tag.name for tag in self._db.query(Tag).all()]}

    def add_comment(
        self, current_user_id: int, slug: str, comment_request: CommentRequest
    ):
        usr = self._db.query(User).filter(User.id == current_user_id).first()
        if usr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )

        article = self._db.query(Article).filter(Article.slug == slug).first()
        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="article not found"
            )
        article.commentsCount += 1

        created_at = datetime.now()
        comment = Comment(id=article.commentsCount, body=comment_request.comment.body)
        comment.createdAt = created_at
        comment.updatedAt = created_at

        comment.article = article
        comment.author = usr

        self._db.add(comment)
        self._db.commit()
        self._db.refresh(comment)

        return CommentResponse(
            comment=CommentResponseInner(
                id=comment.id,
                createdAt=comment.createdAt,
                updatedAt=comment.updatedAt,
                body=comment.body,
                author=ProfileModel(
                    username=usr.username,
                    bio=usr.bio,
                    image=usr.image,
                    following=False,
                ),
            )
        )

    def delete_comment(self, slug: str, id: int):
        article = self._db.query(Article).filter(Article.slug == slug).first()
        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="article not found"
            )

        comment = (
            self._db.query(Comment)
            .filter(Comment.articleSlug == slug, Comment.id == id)
            .first()
        )

        if comment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="comment not found"
            )

        self._db.delete(comment)
        self._db.commit()
