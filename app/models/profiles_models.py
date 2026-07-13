from typing import Annotated

from pydantic import BaseModel, Field


class ProfileModel(BaseModel):
    username: Annotated[str, Field(min_length=1, max_length=255)]
    bio: Annotated[str | None, Field(min_length=1, max_length=255, default=None)]
    image: str | None = None
    following: bool = False


class ProfileResponse(BaseModel):
    profile: ProfileModel
