# backend/app/auth.py

from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import pyotp
from fastapi import HTTPException, status
from .config import settings

# Create bcrypt context with manual backend to avoid passlib version detection issues
import bcrypt as _bcrypt

class BcryptContext:
    """Simple bcrypt wrapper to avoid passlib version detection issues"""
    
    def hash(self, password: str) -> str:
        """Hash password using bcrypt directly"""
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')
    
    def verify(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return _bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

pwd_context = BcryptContext()
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    # Truncate password to 72 bytes to avoid bcrypt limitation
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    # Truncate password to 72 bytes to avoid bcrypt limitation
    if len(plain.encode('utf-8')) > 72:
        plain = plain[:72]
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "iat": now.timestamp(), "exp": expire.timestamp()}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def get_totp_uri(secret: str, email: str, issuer_name: str = "DSM") -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer_name)


def verify_totp(token: str, secret: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)

