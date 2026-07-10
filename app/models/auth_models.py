from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class UserRegistrationRequest(BaseModel):
    username: Annotated[str, Field(min_length=1, max_length=255)]
    password: Annotated[str, Field(min_length=1)]
    email: EmailStr


class RegistrationRequest(BaseModel):
    user: UserRegistrationRequest


class UserResponse(BaseModel):
    email: EmailStr
    token: str
    username: Annotated[str, Field(min_length=1, max_length=255)]
    bio: Annotated[str | None, Field(min_length=1, max_length=255, default=None)]
    image: str | None = None


class AuthResponse(BaseModel):
    user: UserResponse


class UserSignInRequest(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=1)]


class SignInRequest(BaseModel):
    user: UserSignInRequest
