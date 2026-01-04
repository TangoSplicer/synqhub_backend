"""Webhook management and event delivery service."""

import hashlib
import hmac
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Webhook, WebhookEvent, AuditLog


class WebhookService:
    """Manage webhooks and event delivery."""

    # Supported events
    SUPPORTED_EVENTS = [
        "job.submitted",
        "job.started",
        "job.completed",
        "job.failed",
        "circuit.synthesized",
        "circuit.transpiled",
        "plugin.registered",
        "plugin.reviewed",
    ]

    @staticmethod
    async def create_webhook(
        db: AsyncSession,
        user_id: str,
        url: str,
        events: List[str],
        secret: str,
        headers: Optional[Dict[str, str]] = None,
        retry_policy: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a webhook subscription.
        
        Args:
            db: Database session
            user_id: User ID
            url: Webhook URL
            events: List of events to subscribe to
            secret: Webhook secret for HMAC signing
            headers: Custom headers
            retry_policy: Retry configuration
            
        Returns:
            Created webhook info
        """
        try:
            # Validate events
            invalid_events = set(events) - set(WebhookService.SUPPORTED_EVENTS)
            if invalid_events:
                return {
                    "error": f"Invalid events: {invalid_events}",
                    "success": False,
                }
            
            # Default retry policy
            if not retry_policy:
                retry_policy = {
                    "max_retries": 3,
                    "initial_delay": 60,
                    "backoff_multiplier": 2,
                }
            
            webhook = Webhook(
                user_id=user_id,
                url=url,
                events=events,
                secret=secret,
                headers=headers or {},
                retry_policy=retry_policy,
            )
            
            db.add(webhook)
            await db.commit()
            await db.refresh(webhook)
            
            return {
                "webhook_id": webhook.id,
                "url": webhook.url,
                "events": webhook.events,
                "is_active": webhook.is_active,
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def list_webhooks(
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        """List user's webhooks.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of webhooks
        """
        try:
            result = await db.execute(
                select(Webhook).where(Webhook.user_id == user_id)
            )
            webhooks = result.scalars().all()
            
            return {
                "webhooks": [
                    {
                        "id": w.id,
                        "url": w.url,
                        "events": w.events,
                        "is_active": w.is_active,
                        "created_at": w.created_at.isoformat(),
                        "last_triggered_at": w.last_triggered_at.isoformat() if w.last_triggered_at else None,
                    }
                    for w in webhooks
                ],
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def delete_webhook(
        db: AsyncSession,
        webhook_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """Delete a webhook.
        
        Args:
            db: Database session
            webhook_id: Webhook ID
            user_id: User ID
            
        Returns:
            Deletion result
        """
        try:
            result = await db.execute(
                select(Webhook).where(
                    Webhook.id == webhook_id,
                    Webhook.user_id == user_id,
                )
            )
            webhook = result.scalar_one_or_none()
            
            if not webhook:
                return {
                    "error": "Webhook not found",
                    "success": False,
                }
            
            await db.delete(webhook)
            await db.commit()
            
            return {
                "webhook_id": webhook_id,
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def trigger_event(
        db: AsyncSession,
        event_type: str,
        event_data: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        """Trigger a webhook event.
        
        Args:
            db: Database session
            event_type: Type of event
            event_data: Event payload
            user_id: User ID
            
        Returns:
            Trigger result
        """
        try:
            # Find matching webhooks
            result = await db.execute(
                select(Webhook).where(
                    Webhook.user_id == user_id,
                    Webhook.is_active == True,
                )
            )
            webhooks = result.scalars().all()
            
            triggered_count = 0
            for webhook in webhooks:
                if event_type in webhook.events:
                    # Create event log
                    event = WebhookEvent(
                        webhook_id=webhook.id,
                        event_type=event_type,
                        event_data=event_data,
                        status="PENDING",
                    )
                    db.add(event)
                    triggered_count += 1
            
            await db.commit()
            
            return {
                "triggered_count": triggered_count,
                "success": True,
            }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def deliver_event(
        db: AsyncSession,
        event_id: str,
    ) -> Dict[str, Any]:
        """Deliver a webhook event.
        
        Args:
            db: Database session
            event_id: Event ID
            
        Returns:
            Delivery result
        """
        try:
            # Get event
            event_result = await db.execute(
                select(WebhookEvent).where(WebhookEvent.id == event_id)
            )
            event = event_result.scalar_one_or_none()
            
            if not event:
                return {
                    "error": "Event not found",
                    "success": False,
                }
            
            # Get webhook
            webhook_result = await db.execute(
                select(Webhook).where(Webhook.id == event.webhook_id)
            )
            webhook = webhook_result.scalar_one_or_none()
            
            if not webhook:
                return {
                    "error": "Webhook not found",
                    "success": False,
                }
            
            # Prepare payload
            payload = {
                "id": event.id,
                "type": event.event_type,
                "data": event.event_data,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # Sign payload
            signature = WebhookService._sign_payload(
                json.dumps(payload),
                webhook.secret,
            )
            
            # Deliver event
            headers = webhook.headers or {}
            headers["X-Webhook-Signature"] = signature
            headers["Content-Type"] = "application/json"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        webhook.url,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as response:
                        response_body = await response.text()
                        
                        # Update event
                        await db.execute(
                            update(WebhookEvent).where(
                                WebhookEvent.id == event_id
                            ).values(
                                status="DELIVERED" if response.status < 400 else "FAILED",
                                response_status=response.status,
                                response_body=response_body[:5000],
                                sent_at=datetime.utcnow(),
                            )
                        )
                        
                        # Update webhook last triggered
                        await db.execute(
                            update(Webhook).where(
                                Webhook.id == webhook.id
                            ).values(
                                last_triggered_at=datetime.utcnow()
                            )
                        )
                        
                        await db.commit()
                        
                        return {
                            "event_id": event_id,
                            "status": response.status,
                            "success": response.status < 400,
                        }
            except Exception as delivery_error:
                # Mark as failed
                await db.execute(
                    update(WebhookEvent).where(
                        WebhookEvent.id == event_id
                    ).values(
                        status="FAILED",
                        response_body=str(delivery_error)[:5000],
                    )
                )
                await db.commit()
                
                return {
                    "error": str(delivery_error),
                    "success": False,
                }
        except Exception as e:
            await db.rollback()
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    def _sign_payload(payload: str, secret: str) -> str:
        """Sign payload with HMAC-SHA256.
        
        Args:
            payload: Payload to sign
            secret: Secret key
            
        Returns:
            Signature
        """
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    async def get_event_logs(
        db: AsyncSession,
        webhook_id: str,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Get event logs for a webhook.
        
        Args:
            db: Database session
            webhook_id: Webhook ID
            limit: Maximum results
            
        Returns:
            Event logs
        """
        try:
            result = await db.execute(
                select(WebhookEvent)
                .where(WebhookEvent.webhook_id == webhook_id)
                .order_by(WebhookEvent.created_at.desc())
                .limit(limit)
            )
            events = result.scalars().all()
            
            return {
                "events": [
                    {
                        "id": e.id,
                        "event_type": e.event_type,
                        "status": e.status,
                        "response_status": e.response_status,
                        "retry_count": e.retry_count,
                        "created_at": e.created_at.isoformat(),
                        "sent_at": e.sent_at.isoformat() if e.sent_at else None,
                    }
                    for e in events
                ],
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }


class AuditLogService:
    """Manage audit logs for compliance."""

    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "SUCCESS",
        error_message: Optional[str] = None,
    ) -> None:
        """Log an action for audit trail.
        
        Args:
            db: Database session
            user_id: User ID
            action: Action performed
            resource_type: Type of resource
            resource_id: Resource ID
            changes: Changes made
            ip_address: Client IP address
            user_agent: User agent string
            status: Action status
            error_message: Error message if failed
        """
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                changes=changes,
                ip_address=ip_address,
                user_agent=user_agent,
                status=status,
                error_message=error_message,
            )
            db.add(audit_log)
            await db.commit()
        except Exception as e:
            print(f"Failed to log audit: {e}")
            await db.rollback()

    @staticmethod
    async def get_audit_logs(
        db: AsyncSession,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get audit logs for a user.
        
        Args:
            db: Database session
            user_id: User ID
            limit: Maximum results
            offset: Pagination offset
            
        Returns:
            Audit logs
        """
        try:
            result = await db.execute(
                select(AuditLog)
                .where(AuditLog.user_id == user_id)
                .order_by(AuditLog.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            logs = result.scalars().all()
            
            return {
                "logs": [
                    {
                        "id": log.id,
                        "action": log.action,
                        "resource_type": log.resource_type,
                        "resource_id": log.resource_id,
                        "status": log.status,
                        "created_at": log.created_at.isoformat(),
                    }
                    for log in logs
                ],
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }
