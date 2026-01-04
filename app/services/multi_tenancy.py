"""Multi-tenancy support service."""

from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class TenantService:
    """Manage multi-tenant organizations."""

    @staticmethod
    async def create_tenant(
        db: AsyncSession,
        name: str,
        owner_id: str,
        plan: str = "free",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new tenant (organization).
        
        Args:
            db: Database session
            name: Organization name
            owner_id: Owner user ID
            plan: Subscription plan
            metadata: Additional metadata
            
        Returns:
            Tenant info
        """
        try:
            from app.models import Tenant
            
            tenant = Tenant(
                id=str(uuid4()),
                name=name,
                owner_id=owner_id,
                plan=plan,
                metadata=metadata or {},
                is_active=True,
            )
            
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)
            
            return {
                "tenant_id": tenant.id,
                "name": tenant.name,
                "plan": tenant.plan,
                "created_at": tenant.created_at.isoformat(),
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def add_member(
        db: AsyncSession,
        tenant_id: str,
        user_id: str,
        role: str = "member",
    ) -> Dict[str, Any]:
        """Add member to tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            user_id: User ID
            role: Member role (owner, admin, member, viewer)
            
        Returns:
            Membership info
        """
        try:
            from app.models import TenantMember
            
            member = TenantMember(
                id=str(uuid4()),
                tenant_id=tenant_id,
                user_id=user_id,
                role=role,
            )
            
            db.add(member)
            await db.commit()
            await db.refresh(member)
            
            return {
                "member_id": member.id,
                "tenant_id": tenant_id,
                "user_id": user_id,
                "role": role,
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def list_members(
        db: AsyncSession,
        tenant_id: str,
    ) -> Dict[str, Any]:
        """List tenant members.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            
        Returns:
            List of members
        """
        try:
            from app.models import TenantMember
            
            result = await db.execute(
                select(TenantMember).where(TenantMember.tenant_id == tenant_id)
            )
            members = result.scalars().all()
            
            return {
                "members": [
                    {
                        "user_id": m.user_id,
                        "role": m.role,
                        "joined_at": m.created_at.isoformat(),
                    }
                    for m in members
                ],
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def get_user_tenants(
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        """Get tenants for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of tenants
        """
        try:
            from app.models import TenantMember, Tenant
            
            result = await db.execute(
                select(TenantMember).where(TenantMember.user_id == user_id)
            )
            memberships = result.scalars().all()
            
            tenants = []
            for membership in memberships:
                tenant_result = await db.execute(
                    select(Tenant).where(Tenant.id == membership.tenant_id)
                )
                tenant = tenant_result.scalar_one_or_none()
                if tenant:
                    tenants.append({
                        "tenant_id": tenant.id,
                        "name": tenant.name,
                        "plan": tenant.plan,
                        "role": membership.role,
                    })
            
            return {
                "tenants": tenants,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def update_plan(
        db: AsyncSession,
        tenant_id: str,
        plan: str,
    ) -> Dict[str, Any]:
        """Update tenant plan.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            plan: New plan (free, pro, enterprise)
            
        Returns:
            Update result
        """
        try:
            from app.models import Tenant
            
            await db.execute(
                update(Tenant).where(Tenant.id == tenant_id).values(plan=plan)
            )
            await db.commit()
            
            return {
                "tenant_id": tenant_id,
                "plan": plan,
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }


class TenantIsolationService:
    """Ensure data isolation between tenants."""

    @staticmethod
    async def filter_by_tenant(
        query,
        tenant_id: str,
        user_id: str,
    ):
        """Filter query by tenant.
        
        Args:
            query: SQLAlchemy query
            tenant_id: Tenant ID
            user_id: User ID
            
        Returns:
            Filtered query
        """
        # Add tenant_id filter to query
        return query.where(getattr(query.froms[0], "tenant_id") == tenant_id)

    @staticmethod
    async def verify_access(
        db: AsyncSession,
        tenant_id: str,
        user_id: str,
    ) -> bool:
        """Verify user has access to tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            user_id: User ID
            
        Returns:
            True if user has access
        """
        try:
            from app.models import TenantMember
            
            result = await db.execute(
                select(TenantMember).where(
                    TenantMember.tenant_id == tenant_id,
                    TenantMember.user_id == user_id,
                )
            )
            return result.scalar_one_or_none() is not None
        except Exception:
            return False
