"""
WebSocket Router for real-time collaboration endpoints.

Provides WebSocket endpoints for collaborative editing, presence tracking,
and real-time communication.
"""

import logging
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from app.websocket.connection_manager import connection_manager, WebSocketMessage, MessageType
from app.websocket.message_handler import message_handler
from app.security.auth import verify_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/collaboration", tags=["collaboration"])


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, token: str):
    """
    WebSocket endpoint for real-time collaboration.
    
    Clients connect with a session ID and JWT token.
    Messages are routed based on type (edit, presence, comment, etc.)
    """
    try:
        # Verify token
        user_data = verify_token(token)
        if not user_data:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        
        user_id = user_data.get("sub")
        
        # Connect user to session
        connection = await connection_manager.connect(websocket, session_id, user_id)
        if not connection:
            await websocket.close(code=status.WS_1011_SERVER_ERROR)
            return
        
        # Get session
        session = await connection_manager.get_session(session_id)
        
        # Send welcome message with initial state
        welcome_message = WebSocketMessage(
            type=MessageType.SYNC,
            session_id=session_id,
            user_id=user_id,
            timestamp=__import__("datetime").datetime.utcnow(),
            data={
                "content": session.content,
                "version": session.version,
                "participants": session.get_participants(),
                "connection_id": connection.connection_id
            }
        )
        await connection.send_message(welcome_message)
        
        # Broadcast user joined
        join_message = WebSocketMessage(
            type=MessageType.PRESENCE,
            session_id=session_id,
            user_id=user_id,
            timestamp=__import__("datetime").datetime.utcnow(),
            data={
                "presence_type": "user_joined",
                "user_id": user_id,
                "participants": session.get_participants()
            }
        )
        await session.broadcast_message(join_message, connection.connection_id)
        
        # Message loop
        while True:
            try:
                # Receive message
                received_message = await connection.receive_message()
                if not received_message:
                    break
                
                # Process message
                await message_handler.process_message(received_message, connection, session)
            
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in message loop: {e}")
                break
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        # Disconnect user
        if connection:
            await connection_manager.disconnect(connection)
            
            # Broadcast user left
            session = await connection_manager.get_session(session_id)
            if session:
                leave_message = WebSocketMessage(
                    type=MessageType.PRESENCE,
                    session_id=session_id,
                    user_id=user_id,
                    timestamp=__import__("datetime").datetime.utcnow(),
                    data={
                        "presence_type": "user_left",
                        "user_id": user_id,
                        "participants": session.get_participants()
                    }
                )
                await session.broadcast_message(leave_message)


@router.post("/sessions")
async def create_session(
    name: str = "",
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Create a new collaboration session.
    
    Returns session ID and connection details.
    """
    try:
        user_id = current_user.get("sub")
        session_id = str(uuid4())
        
        session = await connection_manager.create_session(session_id, user_id, name)
        
        return JSONResponse({
            "session_id": session_id,
            "name": name,
            "owner_id": user_id,
            "created_at": session.created_at.isoformat(),
            "ws_url": f"/api/v1/collaboration/ws/{session_id}"
        })
    
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Get session details and participant information.
    """
    try:
        session = await connection_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        stats = await connection_manager.get_session_stats(session_id)
        
        return JSONResponse(stats)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session")


@router.get("/sessions")
async def list_sessions(
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    List all active collaboration sessions.
    """
    try:
        sessions = connection_manager.get_all_sessions()
        return JSONResponse({"sessions": sessions})
    
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Delete a collaboration session.
    
    Only the session owner can delete it.
    """
    try:
        session = await connection_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        user_id = current_user.get("sub")
        if session.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Only session owner can delete")
        
        success = await connection_manager.delete_session(session_id)
        if success:
            return JSONResponse({"message": "Session deleted"})
        else:
            raise HTTPException(status_code=500, detail="Failed to delete session")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")


@router.get("/sessions/{session_id}/content")
async def get_session_content(
    session_id: str,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Get the current content of a collaboration session.
    """
    try:
        session = await connection_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return JSONResponse({
            "session_id": session_id,
            "content": session.content,
            "version": session.version,
            "edit_count": len(session.edit_history),
            "comment_count": len(session.comments)
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session content: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session content")


@router.get("/sessions/{session_id}/participants")
async def get_session_participants(
    session_id: str,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Get list of participants in a session.
    """
    try:
        session = await connection_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        participants = session.get_participants()
        
        return JSONResponse({
            "session_id": session_id,
            "participant_count": len(participants),
            "participants": participants
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting participants: {e}")
        raise HTTPException(status_code=500, detail="Failed to get participants")


@router.get("/sessions/{session_id}/history")
async def get_session_history(
    session_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Get edit history for a session.
    """
    try:
        session = await connection_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        history = session.edit_history[offset:offset + limit]
        
        return JSONResponse({
            "session_id": session_id,
            "total_edits": len(session.edit_history),
            "edits": [
                {
                    "user_id": edit.user_id,
                    "timestamp": edit.timestamp.isoformat(),
                    "operation": edit.data.get("operation"),
                    "version": edit.version
                }
                for edit in history
            ]
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get history")


@router.get("/sessions/{session_id}/comments")
async def get_session_comments(
    session_id: str,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Get all comments in a session.
    """
    try:
        session = await connection_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return JSONResponse({
            "session_id": session_id,
            "comment_count": len(session.comments),
            "comments": session.comments
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting comments: {e}")
        raise HTTPException(status_code=500, detail="Failed to get comments")


@router.post("/sessions/{session_id}/cleanup")
async def cleanup_session(
    session_id: str,
    current_user: dict = Depends(verify_token)
) -> JSONResponse:
    """
    Clean up inactive connections in a session.
    """
    try:
        session = await connection_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        user_id = current_user.get("sub")
        if session.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Only session owner can cleanup")
        
        await connection_manager.cleanup_inactive_connections()
        
        return JSONResponse({
            "message": "Cleanup completed",
            "active_participants": session.get_participant_count()
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up session: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup session")
