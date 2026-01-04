"""Authentication and authorization utilities."""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import get_settings

settings = get_settings()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """JWT token payload."""

    user_id: str
    email: str
    exp: datetime
    iat: datetime


class Token(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_id: str,
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiration_hours)

    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    email: str,
) -> str:
    """Create JWT refresh token."""
    expires_delta = timedelta(days=settings.jwt_refresh_expiration_days)
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")

        if user_id is None or email is None:
            return None

        return TokenData(
            user_id=user_id,
            email=email,
            exp=datetime.fromtimestamp(payload.get("exp")),
            iat=datetime.fromtimestamp(payload.get("iat")),
        )
    except JWTError:
        return None


def create_tokens(user_id: str, email: str) -> Token:
    """Create both access and refresh tokens."""
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id, email)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_expiration_hours * 3600,
    )
