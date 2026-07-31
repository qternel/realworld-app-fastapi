from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from .database import Base

user_article = Table(
    "users_articles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, index=True, unique=True)
    email = Column(String, unique=True)
    bio = Column(String, nullable=True)
    image = Column(String, nullable=True)
    hashed_password = Column(String)

    followers = relationship(
        "Follower",
        foreign_keys="Follower.owner_id",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    following = relationship(
        "Follower",
        foreign_keys="Follower.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )

    articles = relationship(
        "Article",
        foreign_keys="Article.authorId",
        back_populates="author",
        cascade="all, delete-orphan",
    )

    favorite_articles = relationship(
        "Article", secondary=user_article, back_populates="favorited_by"
    )

    comments = relationship(
        "Comment",
        foreign_keys="Comment.authorId",
        back_populates="author",
        cascade="all, delete-orphan",
    )


class Follower(Base):
    __tablename__ = "followers"
    owner_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    __table_args__ = (CheckConstraint("owner_id != follower_id"),)

    owner = relationship("User", foreign_keys=[owner_id], back_populates="followers")

    follower = relationship(
        "User", foreign_keys=[follower_id], back_populates="following"
    )


article_tag = Table(
    "articles_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(String)
    body = Column(String)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    favoritesCount = Column(Integer, default=0)
    commentsCount = Column(Integer, default=0)
    authorId = Column(Integer, ForeignKey("users.id"))

    author = relationship("User", foreign_keys=[authorId], back_populates="articles")

    favorited_by = relationship(
        "User", secondary=user_article, back_populates="favorite_articles"
    )

    comments = relationship(
        "Comment",
        foreign_keys="Comment.articleSlug",
        back_populates="article",
        cascade="all, delete-orphan",
    )

    tags = relationship(
        "Tag",
        secondary=article_tag,
        back_populates="articles",
    )


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    articles = relationship("Article", secondary=article_tag, back_populates="tags")


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    articleSlug = Column(String, ForeignKey("articles.slug"), primary_key=True)
    body = Column(String)
    authorId = Column(Integer, ForeignKey("users.id"))
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)

    author = relationship("User", foreign_keys=[authorId], back_populates="comments")
    article = relationship(
        "Article", foreign_keys=[articleSlug], back_populates="comments"
    )
