from sqlalchemy import Column, Integer, String

from .database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    email = Column(String, unique=True)
    bio = Column(String, nullable=True)
    image = Column(String, nullable=True)
    hashed_password = Column(String)


class Followers(Base):
    __tablename__ = "followers"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, index=True)
    follower_id = Column(Integer, index=True)
