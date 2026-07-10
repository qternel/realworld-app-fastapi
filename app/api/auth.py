from typing import Annotated

from db.utils import get_db
from fastapi import APIRouter, Depends
from jose import jwt
from models.auth_models import AuthResponse, RegistrationRequest, SignInRequest
from services.auth_service import AuthService
from starlette import status

router = APIRouter()


@router.post(
    "/api/users",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse,
)
async def register_user(
    registration_request: RegistrationRequest,
    auth_service: Annotated[AuthService, Depends()],
):
    return auth_service.register_user(registration_request)


@router.post(
    "/api/users/login", status_code=status.HTTP_200_OK, response_model=AuthResponse
)
async def sign_user_in(
    sign_in_request: SignInRequest, auth_service: Annotated[AuthService, Depends()]
):
    return auth_service.sign_in(sign_in_request)
