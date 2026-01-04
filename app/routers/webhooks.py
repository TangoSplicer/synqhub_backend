"""Webhook management endpoints."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import TokenData
from app.security.auth import get_current_user
from app.services.webhooks import WebhookService, AuditLogService

router = APIRouter(prefix="/api/v1/webhooks", tags=["webhooks"])


@router.post("/subscribe")
async def create_webhook(
    url: str,
    events: List[str],
    secret: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Create a webhook subscription."""
    result = await WebhookService.create_webhook(
        db=db,
        user_id=current_user.user_id,
        url=url,
        events=events,
        secret=secret,
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to create webhook"),
        )
    
    # Log action
    await AuditLogService.log_action(
        db=db,
        user_id=current_user.user_id,
        action="create_webhook",
        resource_type="webhook",
        resource_id=result["webhook_id"],
    )
    
    return result


@router.get("/list")
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """List user's webhooks."""
    result = await WebhookService.list_webhooks(
        db=db,
        user_id=current_user.user_id,
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to list webhooks"),
        )
    
    return result


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Delete a webhook."""
    result = await WebhookService.delete_webhook(
        db=db,
        webhook_id=webhook_id,
        user_id=current_user.user_id,
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.get("error", "Webhook not found"),
        )
    
    # Log action
    await AuditLogService.log_action(
        db=db,
        user_id=current_user.user_id,
        action="delete_webhook",
        resource_type="webhook",
        resource_id=webhook_id,
    )
    
    return result


@router.get("/{webhook_id}/events")
async def get_webhook_events(
    webhook_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    """Get event logs for a webhook."""
    result = await WebhookService.get_event_logs(
        db=db,
        webhook_id=webhook_id,
        limit=limit,
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Failed to get event logs"),
        )
    
    return result
