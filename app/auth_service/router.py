from fastapi import APIRouter, HTTPException, status
from auth_service.schemas import LoginRequest, RegisterRequest, TokenResponse
from core.jwt_auth import (
    authenticate_user,
    create_access_token,
    register_user,
    UserAlreadyExists,
)

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    user = authenticate_user(body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token(user["username"])

    return TokenResponse(access_token=token)

@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest):
    try:
        user = register_user(body.username, body.password, body.full_name)
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    token = create_access_token(user["username"])
    return TokenResponse(access_token=token)