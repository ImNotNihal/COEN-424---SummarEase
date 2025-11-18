from fastapi import APIRouter, HTTPException, status

from auth_service.schemas import LoginRequest, TokenResponse
from core.jwt_auth import authenticate_user, create_access_token

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
