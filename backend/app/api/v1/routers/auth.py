from fastapi import APIRouter
from app.api.v1.controllers.auth import AuthControllerDep
from app.api.v1.models.auth import TokenResponse, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    controller: AuthControllerDep,
) -> TokenResponse:
    return await controller.authenticate_and_create_token(
        email=data.email,
        password=data.password,
    )