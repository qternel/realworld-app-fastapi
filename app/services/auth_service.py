from datetime import datetime, timedelta, timezone
from typing import Annotated

import bcrypt
from db.db_models import User
from db.utils import get_db
from fastapi import Depends, Header, HTTPException
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from models.auth_models import (
    AuthResponse,
    RegistrationRequest,
    SignInRequest,
    UserResponse,
)
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

SECRET_KEY = "ABDASDASDIWEFJ349RF342JF0934"
ALGORITHM = "HS256"


class AuthService:

    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        self._db = db

    def register_user(self, registration_request: RegistrationRequest):
        usr = (
            self._db.query(User)
            .filter(
                or_(
                    User.username == registration_request.user.username,
                    User.email == registration_request.user.email,
                )
            )
            .first()
        )
        if usr is not None:
            if usr.username == registration_request.user.username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="user with this username already exists",
                )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="user with this email already exists",
            )

        hashed_password = bcrypt.hashpw(
            registration_request.user.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        user_model = User(
            username=registration_request.user.username,
            email=registration_request.user.email,
            hashed_password=hashed_password,
        )

        try:
            self._db.add(user_model)
            self._db.commit()
            self._db.refresh(user_model)
        except SQLAlchemyError:
            self._db.rollback()
            raise
        token = self.create_jwt_token(
            payload={"sub": str(user_model.id), "username": user_model.username},
            expires_in=120,
        )
        return AuthResponse(
            user=UserResponse(
                email=user_model.email,
                token=token,
                username=user_model.username,
                bio=user_model.bio,
                image=user_model.image,
            )
        )

    def sign_in(self, sign_in_request: SignInRequest):
        usr = (
            self._db.query(User)
            .filter(User.email == sign_in_request.user.email)
            .first()
        )
        if usr is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user with this email does not exist",
            )
        pwd = sign_in_request.user.password.encode("utf-8")
        pwd_hashed = usr.hashed_password.encode("utf-8")
        if not bcrypt.checkpw(pwd, pwd_hashed):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong password"
            )

        token = self.create_jwt_token(
            payload={"sub": str(usr.id), "username": usr.username},
            expires_in=120,
        )

        return AuthResponse(
            user=UserResponse(
                email=usr.email,
                token=token,
                username=usr.username,
                bio=usr.bio,
                image=usr.image,
            )
        )

    @staticmethod
    def create_jwt_token(payload: dict, expires_in=60):
        payload_jwt = payload.copy()
        exp = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
        payload_jwt.update({"exp": exp})
        return jwt.encode(payload_jwt, SECRET_KEY, algorithm=ALGORITHM)


header_scheme_required = APIKeyHeader(name="Authorization", auto_error=True)
header_scheme_optional = APIKeyHeader(name="Authorization", auto_error=False)


def _check_jwt_helper(authorization: str | None):
    token = authorization
    if token is None:
        return None

    parts = token.split()
    # print(parts)
    if len(parts) != 2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="")

    if parts[0].casefold() != "token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong token type"
        )

    try:
        payload = jwt.decode(parts[1], SECRET_KEY, ALGORITHM)
        return payload
    except JWTError:
        raise 


def check_jwt_required(authorization: Annotated[str, Depends(header_scheme_required)]):
    return _check_jwt_helper(authorization)


def check_jwt_optional(authorization: Annotated[str, Depends(header_scheme_optional)]):
    return _check_jwt_helper(authorization)
