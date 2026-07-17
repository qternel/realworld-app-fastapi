from typing import Annotated

import bcrypt
from db.db_models import Users
from db.utils import get_db
from fastapi import Depends, HTTPException
from jose import jwt
from models.auth_models import AuthResponse, UserResponse
from models.user_models import UpdatedUser, UpdateRequest
from sqlalchemy.orm import Session
from starlette import status

from .auth_service import ALGORITHM, SECRET_KEY


class UserService:
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self._db = db

    def get_current_user(self, payload: dict):
        usr = self._db.query(Users).filter(Users.id == int(payload.get("sub"))).first()

        return AuthResponse(
            user=UserResponse(
                email=usr.email,
                token=jwt.encode(payload, SECRET_KEY, ALGORITHM),
                username=usr.username,
                bio=usr.bio,
                image=usr.image,
            )
        )

    def update_user(self, payload: dict, update_request: UpdateRequest):
        user_id = int(payload.get("sub"))
        usr = self._db.query(Users).filter(Users.id == user_id).first()
        if len(payload) > 0: #
            if update_request.user.email is not None:
                if self._db.query(Users.email == update_request.user.email) is not None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="user with this email already exists",
                    )
                usr.email = update_request.user.email
            if update_request.user.username is not None:
                if (
                    self._db.query(Users.username == update_request.user.username)
                    is not None
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="user with this username already exists",
                    )
                usr.username = update_request.user.username
            if update_request.user.password is not None:
                usr.hashed_password = bcrypt.hashpw(
                    update_request.user.password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8")
            if update_request.user.image is not None:
                usr.image = str(update_request.user.image)
            if update_request.user.bio is not None:
                usr.bio = update_request.user.bio

            self._db.add(usr)
            self._db.commit()
        return AuthResponse(
            user=UserResponse(
                email=usr.email,
                token=jwt.encode(payload, SECRET_KEY, ALGORITHM),
                username=usr.username,
                bio=usr.bio,
                image=usr.image,
            )
        )
