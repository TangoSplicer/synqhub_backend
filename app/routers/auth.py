"""Authentication router."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status

from app.database import get_db
from app.models import User
from app.schemas import (
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.security import (
    create_tokens,
    hash_password,
    verify_password,
    verify_token,
)

router = APIRouter(prefix=\"/auth\", tags=[\"authentication\"])


@router.post(\"/register\", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    \"\"\"Register a new user.\"\"\"
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=\"Email already registered\",
        )

    # Create new user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        organization_id=request.organization,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create tokens
    tokens = create_tokens(user.id, user.email)
    return tokens


@router.post(\"/login\", response_model=TokenResponse)
async def login(
    request: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    \"\"\"Login user.\"\"\"
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Invalid email or password\",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=\"User account is inactive\",
        )

    # Create tokens
    tokens = create_tokens(user.id, user.email)
    return tokens


@router.post(\"/refresh\", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    \"\"\"Refresh access token.\"\"\"
    # Verify refresh token
    token_data = verify_token(request.refresh_token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Invalid or expired refresh token\",
        )

    # Get user
    result = await db.execute(select(User).where(User.id == token_data.user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"User not found or inactive\",
        )

    # Create new tokens
    tokens = create_tokens(user.id, user.email)
    return tokens


@router.get(\"/me\", response_model=UserResponse)
async def get_current_user(
    token: str = Depends(verify_token),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    \"\"\"Get current user profile.\"\"\"
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=\"Invalid or expired token\",
        )

    result = await db.execute(select(User).where(User.id == token.user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=\"User not found\",
        )

    return UserResponse.from_orm(user)
