# backend/app/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .db import get_db
from .auth import decode_access_token
from . import crud, models

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


def get_db_dep():
    yield from get_db()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db_dep)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email:
            raise credentials_exception
        user = crud.CRUDUser.get_by_email(db, email)
        if not user or not user.is_active:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception


def require_superuser(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient privileges")
    return current_user


def _verify_ws_token(token: str | None) -> bool:
    """Validate JWT token or WS_TOKEN passed as query param for WebSocket auth."""
    from .config import settings
    if not token:
        return False

    # Check WS_TOKEN (service-to-service bypass)
    ws_token = getattr(settings, "WS_TOKEN", "")
    if ws_token and token == ws_token:
        return True

    # Primary: JWT validation
    try:
        payload = decode_access_token(token)
        return bool(payload.get("sub"))
    except Exception:
        return False
