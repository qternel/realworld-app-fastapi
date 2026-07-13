from typing import Annotated

from fastapi import APIRouter, Depends, Path
from models.profiles_models import ProfileResponse
from services.auth_service import check_jwt_optional, check_jwt_required
from services.profiles_service import ProfilesService
from starlette import status

router = APIRouter()


@router.get(
    "/api/profiles/{username}",
    status_code=status.HTTP_200_OK,
    response_model=ProfileResponse,
)
async def get_profile(
    username: Annotated[str, Path(min_length=1)],
    profiles_service: Annotated[ProfilesService, Depends()],
    payload: Annotated[dict | None, Depends(check_jwt_optional)],
):
    current_user_id = None if payload is None else int(payload.get("sub"))
    return profiles_service.get_profile(username, current_user_id)


@router.post(
    "/api/profiles/{username}/follow",
    status_code=status.HTTP_200_OK,
    response_model=ProfileResponse,
)
async def follow_user(
    username: str,
    payload: Annotated[dict | None, Depends(check_jwt_required)],
    profiles_service: Annotated[ProfilesService, Depends()],
):
    return profiles_service.follow_user(username, int(payload.get("sub")))
