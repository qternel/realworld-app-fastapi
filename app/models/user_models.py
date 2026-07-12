from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class UpdatedUser(BaseModel):
    email: EmailStr | None = None
    username: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    password: Annotated[str | None, Field(min_length=1)] = None
    image: Annotated[str | None, Field(min_length=1, max_length=255)] = None
    bio: Annotated[str | None, Field(min_length=1, max_length=255)] = None


class UpdateRequest(BaseModel):
    user: UpdatedUser
