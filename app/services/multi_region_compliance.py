"""Multi-region compliance and data residency management."""

from typing import Any, Dict, List, Optional
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class DataResidencyManager:
    \"\"\"Manage data residency across regions.\"\"\"

    SUPPORTED_REGIONS = {
        "us-east-1": {
            "name": "US East (N. Virginia)",
            "country": "US",
            "compliance": ["SOC2", "HIPAA", "GDPR"],
        },
        "eu-west-1": {
            "name": "EU (Ireland)",
            "country": "IE",
            "compliance": ["GDPR", "SOC2"],
        },
        "ap-southeast-1": {
            "name": "Asia Pacific (Singapore)",
            "country": "SG",
            "compliance": ["SOC2"],
        },
        "ca-central-1": {
            "name": "Canada (Central)",
            "country": "CA",
            "compliance": ["SOC2", "PIPEDA"],
        },
    }

    async def set_data_residency(
        self,
        db: AsyncSession,
        user_id: str,
        region: str,
    ) -> Dict[str, Any]:
        \"\"\"Set data residency region for user.
        
        Args:
            db: Database session
            user_id: User ID
            region: Region code
            
        Returns:
            Residency configuration
        \"\"\"
        try:
            if region not in self.SUPPORTED_REGIONS:
                return {
                    "error": f"Unsupported region: {region}",
                    "success": False,
                }
            
            from app.models import User
            
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {
                    "error": "User not found",
                    "success": False,
                }
            
            user.data_residency_region = region
            db.add(user)
            await db.commit()
            
            region_info = self.SUPPORTED_REGIONS[region]
            
            return {
                "user_id": user_id,
                "region": region,
                "region_name": region_info["name"],
                "country": region_info["country"],
                "compliance_frameworks": region_info["compliance"],
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    async def get_data_residency(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        \"\"\"Get data residency configuration.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Residency configuration
        \"\"\"
        try:
            from app.models import User
            
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {
                    "error": "User not found",
                    "success": False,
                }
            
            region = user.data_residency_region or "us-east-1"
            region_info = self.SUPPORTED_REGIONS.get(region, {})
            
            return {
                "user_id": user_id,
                "region": region,
                "region_name": region_info.get("name"),
                "country": region_info.get("country"),
                "compliance_frameworks": region_info.get("compliance", []),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def validate_data_residency(
        self,
        db: AsyncSession,
        user_id: str,
        required_country: Optional[str] = None,
    ) -> Dict[str, Any]:
        \"\"\"Validate data residency compliance.
        
        Args:
            db: Database session
            user_id: User ID
            required_country: Required country for data
            
        Returns:
            Validation result
        \"\"\"
        try:
            residency = await self.get_data_residency(db, user_id)
            
            if not residency["success"]:
                return residency
            
            if required_country:
                is_compliant = residency["country"] == required_country
                return {
                    "user_id": user_id,
                    "is_compliant": is_compliant,
                    "required_country": required_country,
                    "actual_country": residency["country"],
                    "success": True,
                }
            
            return {
                "user_id": user_id,
                "is_compliant": True,
                "residency": residency,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }


class RegionalComplianceManager:
    \"\"\"Manage compliance across regions.\"\"\"

    REGIONAL_REQUIREMENTS = {
        "US": {
            "frameworks": ["SOC2", "HIPAA"],
            "data_retention_days": 2555,  # 7 years
            "encryption_required": True,
            "audit_logging_required": True,
        },
        "EU": {
            "frameworks": ["GDPR", "SOC2"],
            "data_retention_days": 2555,  # 7 years
            "encryption_required": True,
            "audit_logging_required": True,
            "data_subject_rights": ["access", "deletion", "portability"],
        },
        "CA": {
            "frameworks": ["SOC2", "PIPEDA"],
            "data_retention_days": 1825,  # 5 years
            "encryption_required": True,
            "audit_logging_required": True,
        },
        "SG": {
            "frameworks": ["SOC2"],
            "data_retention_days": 1825,  # 5 years
            "encryption_required": True,
            "audit_logging_required": True,
        },
    }

    async def get_regional_requirements(
        self,
        country: str,
    ) -> Dict[str, Any]:
        \"\"\"Get compliance requirements for region.
        
        Args:
            country: Country code
            
        Returns:
            Regional requirements
        \"\"\"
        try:
            requirements = self.REGIONAL_REQUIREMENTS.get(country)
            
            if not requirements:
                return {
                    "error": f"Unknown country: {country}",
                    "success": False,
                }
            
            return {
                "country": country,
                "requirements": requirements,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def check_regional_compliance(
        self,
        db: AsyncSession,
        user_id: str,
        country: str,
    ) -> Dict[str, Any]:
        \"\"\"Check compliance with regional requirements.
        
        Args:
            db: Database session
            user_id: User ID
            country: Country code
            
        Returns:
            Compliance check result
        \"\"\"
        try:
            from app.models import User
            
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return {
                    "error": "User not found",
                    "success": False,
                }
            
            requirements = self.REGIONAL_REQUIREMENTS.get(country, {})
            
            checks = {
                "encryption_enabled": user.encryption_enabled,
                "audit_logging_enabled": True,  # Always enabled
                "mfa_enabled": user.mfa_enabled,
                "ip_whitelist_enabled": user.ip_whitelist_enabled,
            }
            
            compliant_checks = sum(1 for v in checks.values() if v)
            total_checks = len(checks)
            compliance_percentage = (compliant_checks / total_checks * 100) if total_checks > 0 else 0
            
            return {
                "user_id": user_id,
                "country": country,
                "compliance_percentage": compliance_percentage,
                "required_frameworks": requirements.get("frameworks", []),
                "checks": checks,
                "is_compliant": compliance_percentage >= 80,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }


class DataTransferCompliance:
    \"\"\"Manage data transfer compliance across regions.\"\"\"

    async def validate_cross_border_transfer(
        self,
        source_country: str,
        destination_country: str,
    ) -> Dict[str, Any]:
        \"\"\"Validate cross-border data transfer.
        
        Args:
            source_country: Source country code
            destination_country: Destination country code
            
        Returns:
            Transfer validation result
        \"\"\"
        try:
            # Define allowed transfers
            allowed_transfers = {
                "US": ["US", "CA", "SG"],
                "EU": ["EU", "CA"],
                "CA": ["US", "EU", "CA"],
                "SG": ["US", "SG"],
            }
            
            allowed = allowed_transfers.get(source_country, [])
            is_allowed = destination_country in allowed
            
            return {
                "source_country": source_country,
                "destination_country": destination_country,
                "is_allowed": is_allowed,
                "reason": (
                    "Transfer allowed" if is_allowed else
                    "Cross-border transfer restricted by regional compliance"
                ),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def log_data_transfer(
        self,
        db: AsyncSession,
        user_id: str,
        source_region: str,
        destination_region: str,
        data_volume_mb: float,
    ) -> Dict[str, Any]:
        \"\"\"Log data transfer for compliance audit.
        
        Args:
            db: Database session
            user_id: User ID
            source_region: Source region
            destination_region: Destination region
            data_volume_mb: Data volume in MB
            
        Returns:
            Transfer log entry
        \"\"\"
        try:
            from uuid import uuid4
            from app.models import DataTransferLog
            
            transfer_log = DataTransferLog(
                id=str(uuid4()),
                user_id=user_id,
                source_region=source_region,
                destination_region=destination_region,
                data_volume_mb=data_volume_mb,
                timestamp=datetime.utcnow(),
            )
            
            db.add(transfer_log)
            await db.commit()
            await db.refresh(transfer_log)
            
            return {
                "transfer_id": transfer_log.id,
                "source_region": source_region,
                "destination_region": destination_region,
                "data_volume_mb": data_volume_mb,
                "timestamp": transfer_log.timestamp.isoformat(),
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }
