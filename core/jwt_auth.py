from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.firebase import db
import firebase_admin
from firebase_admin import credentials, firestore as fs_mod

JWT_SECRET = "summarease"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

USERS_COLLECTION = "users"

security = HTTPBearer()

class UserAlreadyExists(Exception):
    pass

# get the user info from firebase
def get_user_doc(username: str) -> Optional[Dict[str, Any]]:
    username = username.lower()
    doc = db.collection(USERS_COLLECTION).document(username)
    snap = doc.get()
    if not snap.exists:
        return None
    data = snap.to_dict()
    # au lieu de user_id
    data["username"] = snap.id
    return data

# user registration
def register_user(username: str, password: str, full_name: str) -> Dict[str, Any]:
    existing = get_user_doc(username)
    if existing:
        raise UserAlreadyExists("User already exists")

    doc = {
        "username": username,
        "full_name": full_name,
        "password": password,
        "created_at": fs_mod.firestore.SERVER_TIMESTAMP,
        "last_login_at": fs_mod.firestore.SERVER_TIMESTAMP,
    }

    db.collection(USERS_COLLECTION).document(username).set(doc)

    return {"username": username, "full_name": full_name}

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    # verify the user exists
    user = get_user_doc(username)
    if not user:
        return None

    if user.get("password") != password:
        return None

    # update last_login_at
    db.collection(USERS_COLLECTION).document(username).update(
        {"last_login_at": fs_mod.firestore.SERVER_TIMESTAMP}
    )

    return {
        "username": username,
        "full_name": user.get("full_name", ""),
    }


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

    user = get_user_doc(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return {
        "username": username,
        "full_name": user.get("full_name", ""),
    }
