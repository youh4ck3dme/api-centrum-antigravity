"""
Local authentication system
Independent JWT authentication that works without Neon Auth
"""

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import bcrypt
import jwt
from fastapi import HTTPException, status
from .config import settings

from .auth import hash_password, verify_password, create_access_token, decode_access_token, create_refresh_token, JWT_ALGORITHM

# Alias pre spätnú kompatibilitu
create_local_access_token = create_access_token
decode_local_access_token = decode_access_token

class LocalAuthService:
    """Service for local authentication operations"""
    
    @staticmethod
    def authenticate_user(email: str, password: str, db) -> dict:
        """Authenticate user with email and password"""
        from .crud import CRUDUser
        from .models import User
        
        user = CRUDUser.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        
        # Create access token
        access_token = create_local_access_token(user.email)
        refresh_token = create_refresh_token(user.email)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            # Create new access token
            access_token = create_local_access_token(payload["sub"])
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

# Add to requirements.txt: passlib[bcrypt]