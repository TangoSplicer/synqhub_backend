"""Collaboration service for real-time editing and session management."""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collaboration import (
    CollaborativeSession,
    SessionParticipant,
    CollaborativeEdit,
    SessionComment,
)
from app.models.user import User


class CollaborationService:
    \"\"\"Service for managing collaborative sessions and edits.\"\"\"
    
    @staticmethod
    async def create_session(
        db: AsyncSession,
        title: str,
        created_by: UUID,
        description: Optional[str] = None,
        circuit_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
        max_participants: int = 50,
    ) -> CollaborativeSession:
        \"\"\"Create a new collaborative session.\"\"\"
        session = CollaborativeSession(
            id=uuid4(),
            title=title,
            description=description,
            created_by=created_by,
            circuit_id=circuit_id,
            project_id=project_id,
            max_participants=max_participants,
            is_active=True,
            current_version=0,
        )
        db.add(session)
        await db.flush()
        
        # Add creator as first participant
        await CollaborationService.add_participant(
            db, session.id, created_by, can_edit=True, can_delete=True, can_invite=True
        )
        
        await db.commit()
        return session
    
    @staticmethod
    async def get_session(db: AsyncSession, session_id: UUID) -> Optional[CollaborativeSession]:
        \"\"\"Get a collaborative session by ID.\"\"\"
        result = await db.execute(
            select(CollaborativeSession).where(CollaborativeSession.id == session_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_sessions(
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> List[CollaborativeSession]:
        \"\"\"List collaborative sessions for a user.\"\"\"
        result = await db.execute(
            select(CollaborativeSession)
            .join(SessionParticipant)
            .where(SessionParticipant.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def add_participant(
        db: AsyncSession,
        session_id: UUID,
        user_id: UUID,
        can_edit: bool = True,
        can_delete: bool = False,
        can_invite: bool = False,
    ) -> SessionParticipant:
        \"\"\"Add a participant to a collaborative session.\"\"\"
        participant = SessionParticipant(
            id=uuid4(),
            session_id=session_id,
            user_id=user_id,
            can_edit=can_edit,
            can_delete=can_delete,
            can_invite=can_invite,
            is_online=True,
        )
        db.add(participant)
        await db.commit()
        return participant
    
    @staticmethod
    async def remove_participant(
        db: AsyncSession,
        session_id: UUID,
        user_id: UUID,
    ) -> bool:
        \"\"\"Remove a participant from a collaborative session.\"\"\"
        result = await db.execute(
            select(SessionParticipant).where(
                and_(
                    SessionParticipant.session_id == session_id,
                    SessionParticipant.user_id == user_id,
                )
            )
        )
        participant = result.scalar_one_or_none()
        if participant:
            await db.delete(participant)
            await db.commit()
            return True
        return False
    
    @staticmethod
    async def update_presence(
        db: AsyncSession,
        session_id: UUID,
        user_id: UUID,
        is_online: bool,
        cursor_position: Optional[Dict[str, int]] = None,
        selected_text: Optional[Dict[str, int]] = None,
    ) -> Optional[SessionParticipant]:
        \"\"\"Update user presence in a session.\"\"\"
        result = await db.execute(
            select(SessionParticipant).where(
                and_(
                    SessionParticipant.session_id == session_id,
                    SessionParticipant.user_id == user_id,
                )
            )
        )
        participant = result.scalar_one_or_none()
        if participant:
            participant.is_online = is_online
            participant.cursor_position = cursor_position
            participant.selected_text = selected_text
            participant.last_activity = datetime.utcnow()
            await db.commit()
        return participant
    
    @staticmethod
    async def record_edit(
        db: AsyncSession,
        session_id: UUID,
        user_id: UUID,
        operation: str,
        path: str,
        value: Optional[Dict[str, Any]] = None,
        old_value: Optional[Dict[str, Any]] = None,
    ) -> CollaborativeEdit:
        \"\"\"Record a collaborative edit operation.\"\"\"
        # Get current session version
        session = await CollaborationService.get_session(db, session_id)
        if not session:
            raise ValueError(f\"Session {session_id} not found\")
        
        edit = CollaborativeEdit(
            id=uuid4(),
            session_id=session_id,
            user_id=user_id,
            operation=operation,
            path=path,
            value=value,
            old_value=old_value,
            version=session.current_version,
            timestamp=datetime.utcnow(),
            conflict_resolved=False,
        )
        db.add(edit)
        
        # Increment session version
        session.current_version += 1
        session.updated_at = datetime.utcnow()
        
        await db.commit()
        return edit
    
    @staticmethod\n    async def get_edit_history(\n        db: AsyncSession,\n        session_id: UUID,\n        skip: int = 0,\n        limit: int = 100,\n    ) -> List[CollaborativeEdit]:\n        \"\"\"Get edit history for a session.\"\"\"\n        result = await db.execute(\n            select(CollaborativeEdit)\n            .where(CollaborativeEdit.session_id == session_id)\n            .order_by(CollaborativeEdit.version.desc())\n            .offset(skip)\n            .limit(limit)\n        )\n        return result.scalars().all()\n    \n    @staticmethod\n    async def add_comment(\n        db: AsyncSession,\n        session_id: UUID,\n        user_id: UUID,\n        content: str,\n        code_reference: Optional[str] = None,\n        line_number: Optional[int] = None,\n        parent_comment_id: Optional[UUID] = None,\n    ) -> SessionComment:\n        \"\"\"Add a comment to a session.\"\"\"\n        comment = SessionComment(\n            id=uuid4(),\n            session_id=session_id,\n            user_id=user_id,\n            content=content,\n            code_reference=code_reference,\n            line_number=line_number,\n            parent_comment_id=parent_comment_id,\n            is_resolved=False,\n        )\n        db.add(comment)\n        await db.commit()\n        return comment\n    \n    @staticmethod\n    async def get_comments(\n        db: AsyncSession,\n        session_id: UUID,\n        skip: int = 0,\n        limit: int = 50,\n    ) -> List[SessionComment]:\n        \"\"\"Get comments for a session.\"\"\"\n        result = await db.execute(\n            select(SessionComment)\n            .where(\n                and_(\n                    SessionComment.session_id == session_id,\n                    SessionComment.parent_comment_id.is_(None),  # Top-level comments only\n                )\n            )\n            .order_by(SessionComment.created_at.desc())\n            .offset(skip)\n            .limit(limit)\n        )\n        return result.scalars().all()\n    \n    @staticmethod\n    async def resolve_comment(\n        db: AsyncSession,\n        comment_id: UUID,\n    ) -> Optional[SessionComment]:\n        \"\"\"Mark a comment as resolved.\"\"\"\n        result = await db.execute(\n            select(SessionComment).where(SessionComment.id == comment_id)\n        )\n        comment = result.scalar_one_or_none()\n        if comment:\n            comment.is_resolved = True\n            comment.resolved_at = datetime.utcnow()\n            await db.commit()\n        return comment\n    \n    @staticmethod\n    async def cleanup_inactive_sessions(\n        db: AsyncSession,\n        inactive_hours: int = 24,\n    ) -> int:\n        \"\"\"Clean up inactive collaborative sessions.\"\"\"\n        cutoff_time = datetime.utcnow() - timedelta(hours=inactive_hours)\n        result = await db.execute(\n            select(CollaborativeSession).where(\n                and_(\n                    CollaborativeSession.updated_at < cutoff_time,\n                    CollaborativeSession.is_active.is_(True),\n                )\n            )\n        )\n        sessions = result.scalars().all()\n        for session in sessions:\n            session.is_active = False\n        await db.commit()\n        return len(sessions)\n    \n    @staticmethod\n    async def get_session_stats(\n        db: AsyncSession,\n        session_id: UUID,\n    ) -> Dict[str, Any]:\n        \"\"\"Get statistics for a collaborative session.\"\"\"\n        session = await CollaborationService.get_session(db, session_id)\n        if not session:\n            return {}\n        \n        # Count edits\n        edits_result = await db.execute(\n            select(CollaborativeEdit).where(CollaborativeEdit.session_id == session_id)\n        )\n        edits = edits_result.scalars().all()\n        \n        # Count comments\n        comments_result = await db.execute(\n            select(SessionComment).where(SessionComment.session_id == session_id)\n        )\n        comments = comments_result.scalars().all()\n        \n        return {\n            \"session_id\": session_id,\n            \"title\": session.title,\n            \"participants\": len(session.participants),\n            \"total_edits\": len(edits),\n            \"total_comments\": len(comments),\n            \"current_version\": session.current_version,\n            \"created_at\": session.created_at,\n            \"updated_at\": session.updated_at,\n            \"is_active\": session.is_active,\n        }\n
