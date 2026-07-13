from typing import Annotated

from fastapi import APIRouter, Depends, Path
from services.auth_service import check_jwt_optional
from services.profiles_service import ProfilesService

router = APIRouter()


@router.get("/api/profiles/{username}")
async def get_profile(
    username: Annotated[str, Path(min_length=1)],
    profiles_service: Annotated[ProfilesService, Depends()],
    payload: Annotated[dict | None, Depends(check_jwt_optional)],
):
    current_user_id = None if payload is None else payload.get("sub")
    return profiles_service.get_profile(username, current_user_id)
