"""Advanced authentication and authorization service."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.security.auth import create_access_token, verify_password, hash_password


class AdvancedAuthService:
    """Advanced authentication features."""

    @staticmethod
    async def enable_mfa(
        db: AsyncSession,
        user_id: str,
        mfa_method: str = "totp",
    ) -> Dict[str, Any]:
        """Enable multi-factor authentication.
        
        Args:
            db: Database session
            user_id: User ID
            mfa_method: MFA method (totp, sms, email)
            
        Returns:
            MFA setup info
        """
        try:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {
                    "error": "User not found",
                    "success": False,
                }
            
            # Generate TOTP secret
            import pyotp
            secret = pyotp.random_base32()
            
            # Update user
            await db.execute(
                update(User).where(User.id == user_id).values(
                    mfa_enabled=True,
                    mfa_method=mfa_method,
                    mfa_secret=secret,
                )
            )
            await db.commit()
            
            return {
                "mfa_enabled": True,
                "mfa_method": mfa_method,
                "secret": secret,
                "qr_code_url": f"otpauth://totp/SynQ:{user.email}?secret={secret}&issuer=SynQ",
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def verify_mfa(
        db: AsyncSession,
        user_id: str,
        code: str,
    ) -> Dict[str, Any]:
        """Verify MFA code.
        
        Args:
            db: Database session
            user_id: User ID
            code: MFA code
            
        Returns:
            Verification result
        """
        try:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.mfa_enabled:
                return {
                    "error": "MFA not enabled",
                    "success": False,
                }
            
            # Verify TOTP
            import pyotp
            totp = pyotp.TOTP(user.mfa_secret)
            
            if not totp.verify(code):
                return {
                    "error": "Invalid MFA code",
                    "success": False,
                }
            
            return {
                "verified": True,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def create_api_key(
        db: AsyncSession,
        user_id: str,
        name: str,
        scopes: List[str],
        expires_in_days: int = 365,
    ) -> Dict[str, Any]:
        """Create API key for programmatic access.
        
        Args:
            db: Database session
            user_id: User ID
            name: API key name
            scopes: Allowed scopes
            expires_in_days: Expiration in days
            
        Returns:
            API key info
        """
        try:
            import secrets
            from app.models import APIKey
            
            # Generate key
            key = secrets.token_urlsafe(32)
            key_hash = hash_password(key)
            
            # Create API key record
            api_key = APIKey(
                user_id=user_id,
                name=name,
                key_hash=key_hash,
                scopes=scopes,
                expires_at=datetime.utcnow() + timedelta(days=expires_in_days),
                last_used_at=None,
            )
            
            db.add(api_key)
            await db.commit()
            await db.refresh(api_key)
            
            return {
                "key_id": api_key.id,
                "key": key,  # Only shown once
                "name": api_key.name,
                "scopes": api_key.scopes,
                "expires_at": api_key.expires_at.isoformat(),
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def list_api_keys(
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        """List user's API keys.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of API keys
        """
        try:
            from app.models import APIKey
            
            result = await db.execute(
                select(APIKey).where(APIKey.user_id == user_id)
            )
            keys = result.scalars().all()
            
            return {
                "keys": [
                    {
                        "id": k.id,
                        "name": k.name,
                        "scopes": k.scopes,
                        "created_at": k.created_at.isoformat(),
                        "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
                        "expires_at": k.expires_at.isoformat(),
                    }
                    for k in keys
                ],
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def revoke_api_key(
        db: AsyncSession,
        user_id: str,
        key_id: str,
    ) -> Dict[str, Any]:
        """Revoke an API key.
        
        Args:
            db: Database session
            user_id: User ID
            key_id: API key ID
            
        Returns:
            Revocation result
        """
        try:
            from app.models import APIKey
            
            result = await db.execute(
                select(APIKey).where(
                    APIKey.id == key_id,
                    APIKey.user_id == user_id,
                )
            )
            key = result.scalar_one_or_none()
            
            if not key:
                return {
                    "error": "API key not found",
                    "success": False,
                }
            
            await db.delete(key)
            await db.commit()
            
            return {
                "key_id": key_id,
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }


class RoleBasedAccessControl:
    """Role-based access control (RBAC)."""

    ROLES = {
        "admin": {
            "permissions": [
                "read:*",
                "write:*",
                "delete:*",
                "manage:users",
                "manage:plugins",
            ]
        },
        "user": {
            "permissions": [
                "read:own",
                "write:own",
                "delete:own",
            ]
        },
        "guest": {
            "permissions": [
                "read:public",
            ]
        },
    }

    @staticmethod
    async def assign_role(
        db: AsyncSession,
        user_id: str,
        role: str,
    ) -> Dict[str, Any]:
        """Assign role to user.
        
        Args:
            db: Database session
            user_id: User ID
            role: Role name
            
        Returns:
            Assignment result
        """
        try:
            if role not in RoleBasedAccessControl.ROLES:
                return {
                    "error": f"Unknown role: {role}",
                    "success": False,
                }
            
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {
                    "error": "User not found",
                    "success": False,
                }
            
            await db.execute(
                update(User).where(User.id == user_id).values(role=role)
            )
            await db.commit()
            
            return {
                "user_id": user_id,
                "role": role,
                "permissions": RoleBasedAccessControl.ROLES[role]["permissions"],
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def check_permission(
        db: AsyncSession,
        user_id: str,
        permission: str,
    ) -> bool:
        """Check if user has permission.
        
        Args:
            db: Database session
            user_id: User ID
            permission: Permission to check
            
        Returns:
            True if user has permission
        """
        try:
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            role = user.role or "guest"
            permissions = RoleBasedAccessControl.ROLES.get(role, {}).get("permissions", [])
            
            # Check exact match or wildcard
            return (
                permission in permissions
                or any(p.endswith(":*") for p in permissions)
            )
        except Exception:
            return False
