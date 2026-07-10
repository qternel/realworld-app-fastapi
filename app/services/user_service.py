from typing import Annotated

from db.db_models import Users
from db.utils import get_db
from fastapi import Depends
from jose import jwt
from models.auth_models import AuthResponse, UserResponse
from sqlalchemy.orm import Session

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
