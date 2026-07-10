from typing import Annotated

from fastapi import APIRouter, Depends
from models.auth_models import AuthResponse
from services.auth_service import check_jwt
from services.user_service import UserService
from starlette import status

router = APIRouter()


@router.get("/api/user", status_code=status.HTTP_200_OK, response_model=AuthResponse)
def get_current_user(
    user_service: Annotated[UserService, Depends()],
    payload: Annotated[dict, Depends(check_jwt)],
):
    return user_service.get_current_user(payload)
