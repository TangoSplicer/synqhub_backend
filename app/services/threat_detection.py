"""Advanced threat detection and security monitoring."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class ThreatDetectionEngine:
    """Detect security threats and anomalies."""

    def __init__(self):
        """Initialize threat detection engine."""
        self.threat_levels = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
        }

    async def detect_brute_force_attacks(
        self,
        db: AsyncSession,
        user_id: str,
        time_window_minutes: int = 15,
        threshold: int = 5,
    ) -> Dict[str, Any]:
        """Detect brute force attack attempts.
        
        Args:
            db: Database session
            user_id: User ID
            time_window_minutes: Time window to check
            threshold: Failed attempts threshold
            
        Returns:
            Brute force detection result
        """
        try:
            from app.models import AuditLog
            
            time_window = datetime.utcnow() - timedelta(minutes=time_window_minutes)
            
            # Count failed login attempts
            result = await db.execute(
                select(func.count(AuditLog.id)).where(
                    AuditLog.user_id == user_id,
                    AuditLog.action == "login_failed",
                    AuditLog.created_at >= time_window,
                )
            )
            failed_attempts = result.scalar() or 0
            
            is_attack = failed_attempts >= threshold
            
            return {
                "threat_detected": is_attack,
                "threat_type": "brute_force",
                "failed_attempts": failed_attempts,
                "threshold": threshold,
                "time_window_minutes": time_window_minutes,
                "threat_level": (
                    "critical" if failed_attempts > threshold * 2 else
                    "high" if is_attack else
                    "low"
                ),
                "recommended_action": (
                    "Account locked" if failed_attempts > threshold * 2 else
                    "Enable MFA" if is_attack else
                    "None"
                ),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def detect_unusual_access_patterns(
        self,
        db: AsyncSession,
        user_id: str,
        current_ip: str,
    ) -> Dict[str, Any]:
        """Detect unusual access patterns.
        
        Args:
            db: Database session
            user_id: User ID
            current_ip: Current access IP
            
        Returns:
            Unusual access detection result
        """
        try:
            from app.models import AuditLog
            
            # Get recent IPs
            result = await db.execute(
                select(AuditLog.ip_address, func.count(AuditLog.id).label("count")).where(
                    AuditLog.user_id == user_id,
                    AuditLog.created_at >= datetime.utcnow() - timedelta(days=30),
                ).group_by(AuditLog.ip_address)
                .order_by(func.count(AuditLog.id).desc())
            )
            ip_history = result.all()
            
            known_ips = [ip[0] for ip in ip_history]
            is_new_ip = current_ip not in known_ips
            
            # Check for rapid location changes
            result = await db.execute(
                select(AuditLog.ip_address, AuditLog.created_at).where(
                    AuditLog.user_id == user_id,
                    AuditLog.created_at >= datetime.utcnow() - timedelta(hours=1),
                ).order_by(AuditLog.created_at.desc())
                .limit(2)
            )
            recent_accesses = result.all()
            
            rapid_location_change = (
                len(recent_accesses) >= 2 and
                recent_accesses[0][0] != recent_accesses[1][0]
            )
            
            threat_level = "high" if (is_new_ip and rapid_location_change) else "medium" if is_new_ip else "low"
            
            return {
                "threat_detected": is_new_ip or rapid_location_change,
                "threat_type": "unusual_access",
                "current_ip": current_ip,
                "is_new_ip": is_new_ip,
                "known_ips": known_ips,
                "rapid_location_change": rapid_location_change,
                "threat_level": threat_level,
                "recommended_action": (
                    "Verify identity" if threat_level == "high" else
                    "Monitor activity" if threat_level == "medium" else
                    "None"
                ),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def detect_data_exfiltration(
        self,
        db: AsyncSession,
        user_id: str,
        time_window_minutes: int = 60,
        threshold_gb: float = 1.0,
    ) -> Dict[str, Any]:
        """Detect potential data exfiltration.
        
        Args:
            db: Database session
            user_id: User ID
            time_window_minutes: Time window to check
            threshold_gb: Data transfer threshold in GB
            
        Returns:
            Data exfiltration detection result
        """
        try:
            from app.models import AuditLog
            
            time_window = datetime.utcnow() - timedelta(minutes=time_window_minutes)
            
            # Count data access operations
            result = await db.execute(
                select(func.count(AuditLog.id)).where(
                    AuditLog.user_id == user_id,
                    AuditLog.action.in_(["download", "export", "api_call"]),
                    AuditLog.created_at >= time_window,
                )
            )
            access_count = result.scalar() or 0
            
            # Estimate data volume (rough estimate)
            estimated_data_gb = access_count * 0.01  # 10MB per operation
            
            is_exfiltration = estimated_data_gb > threshold_gb
            
            return {
                "threat_detected": is_exfiltration,
                "threat_type": "data_exfiltration",
                "access_operations": access_count,
                "estimated_data_gb": estimated_data_gb,
                "threshold_gb": threshold_gb,
                "time_window_minutes": time_window_minutes,
                "threat_level": (
                    "critical" if estimated_data_gb > threshold_gb * 2 else
                    "high" if is_exfiltration else
                    "low"
                ),
                "recommended_action": (
                    "Suspend account" if estimated_data_gb > threshold_gb * 2 else
                    "Investigate activity" if is_exfiltration else
                    "None"
                ),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def detect_privilege_escalation(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        """Detect privilege escalation attempts.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Privilege escalation detection result
        """
        try:
            from app.models import AuditLog, User
            
            # Get user's current role
            result = await db.execute(
                select(User.role).where(User.id == user_id)
            )
            current_role = result.scalar() or "user"
            
            # Check for role change attempts
            result = await db.execute(
                select(AuditLog.action, func.count(AuditLog.id).label("count")).where(
                    AuditLog.user_id == user_id,
                    AuditLog.action.like("%role%"),
                    AuditLog.created_at >= datetime.utcnow() - timedelta(days=1),
                ).group_by(AuditLog.action)
            )
            role_changes = result.all()
            
            # Check for admin operation attempts
            result = await db.execute(
                select(func.count(AuditLog.id)).where(
                    AuditLog.user_id == user_id,
                    AuditLog.action.in_(["manage_users", "manage_system", "delete_data"]),
                    AuditLog.created_at >= datetime.utcnow() - timedelta(days=1),
                )
            )
            admin_attempts = result.scalar() or 0
            
            is_escalation = admin_attempts > 0 and current_role != "admin"
            
            return {
                "threat_detected": is_escalation,
                "threat_type": "privilege_escalation",
                "current_role": current_role,
                "role_change_attempts": len(role_changes),
                "admin_operation_attempts": admin_attempts,
                "threat_level": "critical" if is_escalation else "low",
                "recommended_action": (
                    "Revoke access immediately" if is_escalation else
                    "None"
                ),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def get_security_threats(
        self,
        db: AsyncSession,
        user_id: str,
        current_ip: str,
    ) -> Dict[str, Any]:
        """Get all security threats for user.
        
        Args:
            db: Database session
            user_id: User ID
            current_ip: Current access IP
            
        Returns:
            All detected threats
        """
        try:
            threats = []
            
            # Check brute force
            brute_force = await self.detect_brute_force_attacks(db, user_id)
            if brute_force["threat_detected"]:
                threats.append(brute_force)
            
            # Check unusual access
            unusual_access = await self.detect_unusual_access_patterns(db, user_id, current_ip)
            if unusual_access["threat_detected"]:
                threats.append(unusual_access)
            
            # Check data exfiltration
            exfiltration = await self.detect_data_exfiltration(db, user_id)
            if exfiltration["threat_detected"]:
                threats.append(exfiltration)
            
            # Check privilege escalation
            escalation = await self.detect_privilege_escalation(db, user_id)
            if escalation["threat_detected"]:
                threats.append(escalation)
            
            # Calculate overall threat level
            threat_levels = [t.get("threat_level", "low") for t in threats]
            overall_threat = (
                "critical" if "critical" in threat_levels else
                "high" if "high" in threat_levels else
                "medium" if "medium" in threat_levels else
                "low"
            )
            
            return {
                "threats": threats,
                "threat_count": len(threats),
                "overall_threat_level": overall_threat,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }


class SecurityIncidentManager:
    """Manage security incidents."""

    async def create_incident(
        self,
        db: AsyncSession,
        user_id: str,
        threat_type: str,
        severity: str,
        description: str,
    ) -> Dict[str, Any]:
        """Create security incident.
        
        Args:
            db: Database session
            user_id: User ID
            threat_type: Type of threat
            severity: Incident severity
            description: Description
            
        Returns:
            Incident info
        """
        try:
            from uuid import uuid4
            from app.models import SecurityIncident
            
            incident = SecurityIncident(
                id=str(uuid4()),
                user_id=user_id,
                threat_type=threat_type,
                severity=severity,
                description=description,
                status="OPEN",
                created_at=datetime.utcnow(),
            )
            
            db.add(incident)
            await db.commit()
            await db.refresh(incident)
            
            return {
                "incident_id": incident.id,
                "threat_type": threat_type,
                "severity": severity,
                "status": "OPEN",
                "created_at": incident.created_at.isoformat(),
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    async def get_incidents(
        self,
        db: AsyncSession,
        user_id: str,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get security incidents.
        
        Args:
            db: Database session
            user_id: User ID
            status: Filter by status
            
        Returns:
            List of incidents
        """
        try:
            from app.models import SecurityIncident
            
            query = select(SecurityIncident).where(SecurityIncident.user_id == user_id)
            
            if status:
                query = query.where(SecurityIncident.status == status)
            
            result = await db.execute(query)
            incidents = result.scalars().all()
            
            return {
                "incidents": [
                    {
                        "id": i.id,
                        "threat_type": i.threat_type,
                        "severity": i.severity,
                        "status": i.status,
                        "created_at": i.created_at.isoformat(),
                    }
                    for i in incidents
                ],
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }
