"""Collaboration models for real-time editing and session management."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class CollaborativeSession(Base):
    """Represents a collaborative editing session for circuits or code."""
    
    __tablename__ = "collaborative_sessions"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    circuit_id = Column(PG_UUID(as_uuid=True), ForeignKey("circuits.id"), nullable=True)
    project_id = Column(PG_UUID(as_uuid=True), nullable=True, index=True)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Session metadata
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    max_participants = Column(Integer, default=50, nullable=False)
    
    # Version control
    current_version = Column(Integer, default=0, nullable=False)
    
    # Relationships
    circuit = relationship("Circuit", back_populates="collaboration_sessions")
    creator = relationship("User", foreign_keys=[created_by])
    participants = relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")
    edits = relationship("CollaborativeEdit", back_populates="session", cascade="all, delete-orphan")
    comments = relationship("SessionComment", back_populates="session", cascade="all, delete-orphan")


class SessionParticipant(Base):
    """Tracks participants in a collaborative session."""
    
    __tablename__ = "session_participants"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("collaborative_sessions.id"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Presence tracking
    is_online = Column(Boolean, default=True, nullable=False)
    cursor_position = Column(JSON, nullable=True)  # {line, column}
    selected_text = Column(JSON, nullable=True)  # {start, end}
    
    # Permissions
    can_edit = Column(Boolean, default=True, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)
    can_invite = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    session = relationship("CollaborativeSession", back_populates="participants")
    user = relationship("User")


class CollaborativeEdit(Base):
    """Represents a single edit operation in a collaborative session."""
    
    __tablename__ = "collaborative_edits"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("collaborative_sessions.id"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Edit metadata
    operation = Column(String(50), nullable=False)  # "insert", "delete", "modify"
    path = Column(String(500), nullable=False)  # JSON path to edited element
    value = Column(JSON, nullable=True)  # The new value
    old_value = Column(JSON, nullable=True)  # Previous value for undo
    
    # Version control
    version = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Conflict resolution
    conflict_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Relationships
    session = relationship("CollaborativeSession", back_populates="edits")
    editor = relationship("User", foreign_keys=[user_id])


class SessionComment(Base):
    """Represents a comment in a collaborative session."""
    
    __tablename__ = "session_comments"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("collaborative_sessions.id"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Comment content
    content = Column(Text, nullable=False)
    code_reference = Column(String(500), nullable=True)  # JSON path to referenced code
    line_number = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Threading
    parent_comment_id = Column(PG_UUID(as_uuid=True), ForeignKey("session_comments.id"), nullable=True)
    
    # Relationships
    session = relationship("CollaborativeSession", back_populates="comments")
    author = relationship("User")
    replies = relationship("SessionComment", remote_side=[id], cascade="all, delete-orphan")
