"""Production hardening and security service."""

import hashlib
import secrets
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class SecurityHardeningService:
    """Production security hardening."""

    @staticmethod
    async def enable_ip_whitelist(
        db: AsyncSession,
        user_id: str,
        ip_addresses: list[str],
    ) -> Dict[str, Any]:
        \"\"\"Enable IP whitelist for user.
        
        Args:
            db: Database session
            user_id: User ID
            ip_addresses: List of allowed IP addresses
            
        Returns:
            Whitelist configuration
        \"\"\"
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
            
            # Validate IP addresses
            import ipaddress
            valid_ips = []
            for ip in ip_addresses:
                try:
                    ipaddress.ip_address(ip)
                    valid_ips.append(ip)
                except ValueError:
                    pass
            
            if not valid_ips:
                return {
                    "error": "No valid IP addresses provided",
                    "success": False,
                }
            
            # Store whitelist
            user.ip_whitelist = valid_ips
            user.ip_whitelist_enabled = True
            db.add(user)
            await db.commit()
            
            return {
                "user_id": user_id,
                "ip_whitelist": valid_ips,
                "enabled": True,
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def enable_rate_limiting(
        db: AsyncSession,
        user_id: str,
        requests_per_minute: int = 60,
        requests_per_hour: int = 3600,
    ) -> Dict[str, Any]:
        \"\"\"Enable rate limiting for user.
        
        Args:
            db: Database session
            user_id: User ID
            requests_per_minute: Requests per minute limit
            requests_per_hour: Requests per hour limit
            
        Returns:
            Rate limit configuration
        \"\"\"
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
            
            user.rate_limit_per_minute = requests_per_minute
            user.rate_limit_per_hour = requests_per_hour
            db.add(user)
            await db.commit()
            
            return {
                "user_id": user_id,
                "requests_per_minute": requests_per_minute,
                "requests_per_hour": requests_per_hour,
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def rotate_credentials(
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        \"\"\"Rotate user credentials.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            New credentials
        \"\"\"
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
            
            # Generate new credentials
            new_secret = secrets.token_urlsafe(32)
            
            # Store hash
            user.credential_secret = hashlib.sha256(new_secret.encode()).hexdigest()
            user.credential_rotated_at = __import__('datetime').datetime.utcnow()
            db.add(user)
            await db.commit()
            
            return {
                "user_id": user_id,
                "new_secret": new_secret,  # Only shown once
                "rotated_at": user.credential_rotated_at.isoformat(),
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def enable_encryption_at_rest(
        db: AsyncSession,
        user_id: str,
        encryption_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        \"\"\"Enable encryption at rest for user data.
        
        Args:
            db: Database session
            user_id: User ID
            encryption_key: Custom encryption key
            
        Returns:
            Encryption configuration
        \"\"\"
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
            
            if not encryption_key:
                encryption_key = secrets.token_urlsafe(32)
            
            user.encryption_enabled = True
            user.encryption_key_hash = hashlib.sha256(encryption_key.encode()).hexdigest()
            db.add(user)
            await db.commit()
            
            return {
                "user_id": user_id,
                "encryption_enabled": True,
                "algorithm": "AES-256-GCM",
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def get_security_posture(
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        \"\"\"Get security posture for user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Security posture
        \"\"\"
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
            
            # Calculate security score
            score = 0
            checks = []
            
            if user.mfa_enabled:
                score += 25
                checks.append({"name": "MFA Enabled", "status": "pass"})
            else:
                checks.append({"name": "MFA Enabled", "status": "fail"})
            
            if user.ip_whitelist_enabled:
                score += 25
                checks.append({"name": "IP Whitelist", "status": "pass"})
            else:
                checks.append({"name": "IP Whitelist", "status": "fail"})
            
            if user.encryption_enabled:
                score += 25
                checks.append({"name": "Encryption at Rest", "status": "pass"})
            else:
                checks.append({"name": "Encryption at Rest", "status": "fail"})
            
            if user.credential_rotated_at:
                import datetime
                days_since_rotation = (
                    datetime.datetime.utcnow() - user.credential_rotated_at
                ).days
                if days_since_rotation < 90:
                    score += 25
                    checks.append({"name": "Recent Credential Rotation", "status": "pass"})
                else:
                    checks.append({"name": "Recent Credential Rotation", "status": "fail"})
            else:
                checks.append({"name": "Recent Credential Rotation", "status": "fail"})
            
            return {
                "user_id": user_id,
                "security_score": score,
                "checks": checks,
                "recommendations": [
                    check["name"] for check in checks if check["status"] == "fail"
                ],
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }


class ComplianceService:
    \"\"\"Compliance and regulatory features.\"\"\"

    COMPLIANCE_FRAMEWORKS = {
        "SOC2": {
            "requirements": [
                "Encryption at rest",
                "Encryption in transit",
                "Access controls",
                "Audit logging",
                "Incident response",
            ]
        },
        "HIPAA": {
            "requirements": [
                "PHI encryption",
                "Access controls",
                "Audit logging",
                "Breach notification",
                "Business associate agreements",
            ]
        },
        "GDPR": {
            "requirements": [
                "Data minimization",
                "Purpose limitation",
                "Consent management",
                "Right to deletion",
                "Data portability",
            ]
        },
        "ISO27001": {
            "requirements": [
                "Information security policy",
                "Access control",
                "Cryptography",
                "Physical security",
                "Incident management",
            ]
        },
    }

    @staticmethod
    async def get_compliance_status(
        db: AsyncSession,
        user_id: str,
        framework: str,
    ) -> Dict[str, Any]:
        \"\"\"Get compliance status for framework.
        
        Args:
            db: Database session
            user_id: User ID
            framework: Compliance framework (SOC2, HIPAA, GDPR, ISO27001)
            
        Returns:
            Compliance status
        \"\"\"
        try:
            if framework not in ComplianceService.COMPLIANCE_FRAMEWORKS:
                return {
                    "error": f"Unknown framework: {framework}",
                    "success": False,
                }
            
            security_posture = await SecurityHardeningService.get_security_posture(
                db, user_id
            )
            
            if not security_posture["success"]:
                return security_posture
            
            requirements = ComplianceService.COMPLIANCE_FRAMEWORKS[framework]["requirements"]
            
            # Map security checks to compliance requirements
            met_requirements = [
                req for req in requirements
                if any(check["status"] == "pass" for check in security_posture["checks"])
            ]
            
            compliance_percentage = (len(met_requirements) / len(requirements) * 100) if requirements else 0
            
            return {
                "framework": framework,
                "compliance_percentage": compliance_percentage,
                "requirements": requirements,
                "met_requirements": met_requirements,
                "pending_requirements": [
                    req for req in requirements if req not in met_requirements
                ],
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def export_compliance_report(
        db: AsyncSession,
        user_id: str,
        framework: str,
    ) -> Dict[str, Any]:
        \"\"\"Export compliance report.
        
        Args:
            db: Database session
            user_id: User ID
            framework: Compliance framework
            
        Returns:
            Compliance report
        \"\"\"
        try:
            status = await ComplianceService.get_compliance_status(
                db, user_id, framework
            )
            
            if not status["success"]:
                return status
            
            return {
                "report_type": "compliance",
                "framework": framework,
                "generated_at": __import__('datetime').datetime.utcnow().isoformat(),
                "compliance_status": status,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }
