from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from .database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, index=True, unique=True)
    email = Column(String, unique=True)
    bio = Column(String, nullable=True)
    image = Column(String, nullable=True)
    hashed_password = Column(String)

    followers = relationship(
        "Followers",
        foreign_keys="Followers.owner_id",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    following = relationship(
        "Followers",
        foreign_keys="Followers.follower_id",
        back_populates="follower",
        cascade="all, delete-orphan",
    )

    articles = relationship(
        "Articles",
        foreign_keys="Articles.authorId",
        back_populates="author",
        cascade="all, delete-orphan",
    )


class Followers(Base):
    __tablename__ = "followers"
    owner_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    follower_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    __table_args__ = (CheckConstraint("owner_id != follower_id"),)

    owner = relationship("Users", foreign_keys=[owner_id], back_populates="followers")

    follower = relationship(
        "Users", foreign_keys=[follower_id], back_populates="following"
    )


class Articles(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    slug = Column(String, unique=True, index=True)
    title = Column(String)
    description = Column(String)
    body = Column(String)
    tagList = Column(JSON, nullable=True)
    createdAt = Column(DateTime)
    updatedAt = Column(DateTime)
    favorited = Column(Boolean, default=False)
    favoritesCount = Column(Integer, default=0)
    authorId = Column(Integer, ForeignKey("users.id"))

    author = relationship("Users", foreign_keys=[authorId], back_populates="articles")
