from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.models.auth_models import AuthResponse
from app.models.user_models import UpdateRequest
from app.services.auth_service import check_jwt_required
from app.services.user_service import UserService

router = APIRouter()


@router.get("/api/user", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def get_current_user(
    user_service: Annotated[UserService, Depends()],
    payload: Annotated[dict, Depends(check_jwt_required)],
):
    return user_service.get_current_user(payload)


@router.put("/api/user", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def update_user(
    user_service: Annotated[UserService, Depends()],
    payload: Annotated[dict, Depends(check_jwt_required)],
    update_request: UpdateRequest,
):
    return user_service.update_user(payload, update_request)
