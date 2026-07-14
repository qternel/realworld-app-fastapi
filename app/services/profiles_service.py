from typing import Annotated

from db.db_models import Followers, Users
from db.utils import get_db
from fastapi import Depends, HTTPException
from models.profiles_models import ProfileModel, ProfileResponse
from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette import status


class ProfilesService:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self._db = db

    def get_profile(self, username: str, current_user_id: int | None = None):
        usr = self._db.query(Users).filter(Users.username == username).first()
        if usr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user {username} does not exist",
            )
        if current_user_id is not None:
            following = (
                self._db.query(Followers)
                .filter(
                    and_(
                        Followers.owner_id == usr.id,
                        Followers.follower_id == current_user_id,
                    )
                )
                .first()
                is not None
            )
        else:
            following = False

        return ProfileResponse(
            profile=ProfileModel(
                username=usr.username, bio=usr.bio, image=usr.image, following=following
            )
        )

    def follow_user(self, username: str, current_user_id: int):

        usr = self._db.query(Users).filter(Users.username == username).first()
        if usr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user {username} does not exist",
            )

        if current_user_id == usr.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="you're trying to follow yourself",
            )

        following = (
            self._db.query(Followers)
            .filter(
                and_(
                    Followers.owner_id == usr.id,
                    Followers.follower_id == current_user_id,
                )
            )
            .first()
            is not None
        )

        if not following:
            follower = Followers(owner_id=usr.id, follower_id=current_user_id)
            self._db.add(follower)
            self._db.commit()

        return ProfileResponse(
            profile=ProfileModel(
                username=usr.username, bio=usr.bio, image=usr.image, following=True
            )
        )
