"""User request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8, description=\"Password must be at least 8 characters\")
    organization: str | None = None


class UserLoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response."""

    id: str
    email: str
    role: str
    organization_id: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    \"\"\"Token response.\"\"\"

    access_token: str
    refresh_token: str
    token_type: str = \"bearer\"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    \"\"\"Refresh token request.\"\"\"

    refresh_token: str
