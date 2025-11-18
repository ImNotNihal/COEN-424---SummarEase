from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

JWT_SECRET = "summarease"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

#test data
FAKE_USERS_DB = {
    "assane": {
        "username": "assane",
        "password": "test123",
        "full_name": "Assane",
    },
    "nihal": {
        "username": "nihal",
        "password": "nihal321",
        "full_name": "Nihal",
    },
    "ismael": {
        "username": "ismael",
        "password": "ismael321",
        "full_name": "Ismael",
    }
}

security = HTTPBearer()


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    # verify the user exists
    user = FAKE_USERS_DB.get(username)
    if not user:
        return None
    if user["password"] != password:
        return None
    return user


def create_access_token(username: str) -> str:
    #create JWT
    now = datetime.utcnow()
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": username,
        "iat": now,
        "exp": expire,
    }
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:

    #get user from authorization from header
    # auth_header = request.headers.get("Authorization")
    # if not auth_header or not auth_header.startswith("Bearer "):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Missing or invalid Authorization header",
    #     )

    # token = auth_header.split(" ", 1)[1]

    # utilise le truc prebuilt de FastApi
    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = FAKE_USERS_DB.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
