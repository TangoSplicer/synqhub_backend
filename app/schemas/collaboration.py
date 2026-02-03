"""Pydantic schemas for collaboration endpoints."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field


class SessionParticipantBase(BaseModel):
    """Base schema for session participants."""
    
    can_edit: bool = True
    can_delete: bool = False
    can_invite: bool = False


class SessionParticipantCreate(SessionParticipantBase):
    """Schema for creating session participants."""
    
    user_id: UUID


class SessionParticipantResponse(SessionParticipantBase):
    """Schema for session participant responses."""
    
    id: UUID
    session_id: UUID
    user_id: UUID
    joined_at: datetime
    last_activity: datetime
    is_online: bool
    cursor_position: Optional[Dict[str, int]] = None
    selected_text: Optional[Dict[str, int]] = None
    
    class Config:
        from_attributes = True


class CollaborativeSessionBase(BaseModel):
    """Base schema for collaborative sessions."""
    
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    max_participants: int = Field(default=50, ge=1, le=500)


class CollaborativeSessionCreate(CollaborativeSessionBase):
    """Schema for creating collaborative sessions."""
    
    circuit_id: Optional[UUID] = None
    project_id: Optional[UUID] = None


class CollaborativeSessionUpdate(BaseModel):
    """Schema for updating collaborative sessions."""
    
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    max_participants: Optional[int] = None


class CollaborativeSessionResponse(CollaborativeSessionBase):
    """Schema for collaborative session responses."""
    
    id: UUID
    circuit_id: Optional[UUID]
    project_id: Optional[UUID]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    current_version: int
    participants: List[SessionParticipantResponse] = []
    
    class Config:
        from_attributes = True


class CollaborativeEditBase(BaseModel):
    """Base schema for collaborative edits."""
    
    operation: str = Field(..., pattern="^(insert|delete|modify)$")
    path: str = Field(..., min_length=1, max_length=500)
    value: Optional[Dict[str, Any]] = None
    old_value: Optional[Dict[str, Any]] = None


class CollaborativeEditCreate(CollaborativeEditBase):
    """Schema for creating collaborative edits."""
    
    version: int = Field(..., ge=0)


class CollaborativeEditResponse(CollaborativeEditBase):
    """Schema for collaborative edit responses."""
    
    id: UUID
    session_id: UUID
    user_id: UUID
    version: int
    timestamp: datetime
    conflict_resolved: bool
    resolved_by: Optional[UUID] = None
    resolution_notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class SessionCommentBase(BaseModel):
    """Base schema for session comments."""
    
    content: str = Field(..., min_length=1)
    code_reference: Optional[str] = None
    line_number: Optional[int] = None


class SessionCommentCreate(SessionCommentBase):
    """Schema for creating session comments."""
    
    parent_comment_id: Optional[UUID] = None


class SessionCommentResponse(SessionCommentBase):
    """Schema for session comment responses."""
    
    id: UUID
    session_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    is_resolved: bool
    resolved_at: Optional[datetime] = None
    parent_comment_id: Optional[UUID] = None
    replies: List["SessionCommentResponse"] = []
    
    class Config:
        from_attributes = True


# Update forward references
SessionCommentResponse.model_rebuild()


class SessionHistoryResponse(BaseModel):
    """Schema for session history/edit history."""
    
    total_edits: int
    edits: List[CollaborativeEditResponse]
    conflicts_resolved: int
    last_edit_time: Optional[datetime] = None


class SessionPresenceUpdate(BaseModel):
    """Schema for presence updates."""
    
    is_online: bool
    cursor_position: Optional[Dict[str, int]] = None
    selected_text: Optional[Dict[str, int]] = None


class SessionInvitation(BaseModel):
    """Schema for session invitations."""
    
    session_id: UUID
    invited_user_id: UUID
    can_edit: bool = True
    can_delete: bool = False
    can_invite: bool = False
