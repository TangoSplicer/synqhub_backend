"""
WebSocket Connection Manager for real-time collaboration.

Handles WebSocket connections, session management, message routing,
and broadcast operations for collaborative editing.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Callable, Any
from uuid import UUID, uuid4
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ConnectionState(str, Enum):
    """WebSocket connection states."""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"


class MessageType(str, Enum):
    """WebSocket message types."""
    EDIT = "edit"
    PRESENCE = "presence"
    COMMENT = "comment"
    UNDO = "undo"
    REDO = "redo"
    SYNC = "sync"
    ACK = "ack"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


class WebSocketMessage(BaseModel):
    """WebSocket message structure."""
    type: MessageType
    session_id: str
    user_id: str
    timestamp: datetime
    data: Dict[str, Any]
    version: int = 1
    operation_id: Optional[str] = None


class UserConnection:
    """Represents a single user connection."""
    
    def __init__(self, websocket: WebSocket, user_id: str, session_id: str):
        self.websocket = websocket
        self.user_id = user_id
        self.session_id = session_id
        self.connection_id = str(uuid4())
        self.state = ConnectionState.CONNECTING
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.message_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self.pending_operations: Dict[str, Any] = {}
        self.cursor_position = {"line": 0, "column": 0}
        self.selection = {"start": 0, "end": 0}
        self.user_info = {"name": "", "color": ""}
        
    async def send_message(self, message: WebSocketMessage) -> bool:
        """Send a message to the client."""
        try:
            await self.websocket.send_json(message.dict(default=str))
            self.last_activity = datetime.utcnow()
            return True
        except Exception as e:
            logger.error(f"Failed to send message to {self.user_id}: {e}")
            return False
    
    async def receive_message(self) -> Optional[WebSocketMessage]:
        """Receive a message from the client."""
        try:
            data = await self.websocket.receive_json()
            self.last_activity = datetime.utcnow()
            return WebSocketMessage(**data)
        except WebSocketDisconnect:
            self.state = ConnectionState.DISCONNECTED
            return None
        except Exception as e:
            logger.error(f"Failed to receive message from {self.user_id}: {e}")
            return None
    
    def is_active(self, timeout_seconds: int = 300) -> bool:
        """Check if connection is still active."""
        if self.state == ConnectionState.DISCONNECTED:
            return False
        
        time_since_activity = (datetime.utcnow() - self.last_activity).total_seconds()
        return time_since_activity < timeout_seconds
    
    async def close(self) -> None:
        """Close the connection."""
        self.state = ConnectionState.DISCONNECTING
        try:
            await self.websocket.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")
        finally:
            self.state = ConnectionState.DISCONNECTED


class CollaborationSession:
    """Represents a collaboration session."""
    
    def __init__(self, session_id: str, owner_id: str, name: str = ""):
        self.session_id = session_id
        self.owner_id = owner_id
        self.name = name
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.connections: Dict[str, UserConnection] = {}
        self.edit_history: List[WebSocketMessage] = []
        self.comments: List[Dict[str, Any]] = []
        self.content = ""
        self.version = 0
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.lock = asyncio.Lock()
        
    async def add_connection(self, connection: UserConnection) -> bool:
        """Add a user connection to the session."""
        async with self.lock:
            if len(self.connections) >= 100:  # Max 100 participants
                return False
            
            self.connections[connection.connection_id] = connection
            connection.state = ConnectionState.CONNECTED
            self.updated_at = datetime.utcnow()
            logger.info(f"Connection {connection.connection_id} added to session {self.session_id}")
            return True
    
    async def remove_connection(self, connection_id: str) -> None:
        """Remove a user connection from the session."""
        async with self.lock:
            if connection_id in self.connections:
                del self.connections[connection_id]
                self.updated_at = datetime.utcnow()
                logger.info(f"Connection {connection_id} removed from session {self.session_id}")
    
    async def broadcast_message(
        self,
        message: WebSocketMessage,
        exclude_connection_id: Optional[str] = None
    ) -> None:
        """Broadcast a message to all connected users."""
        async with self.lock:
            disconnected = []
            
            for conn_id, connection in self.connections.items():
                if exclude_connection_id and conn_id == exclude_connection_id:
                    continue
                
                if connection.is_active():
                    success = await connection.send_message(message)
                    if not success:
                        disconnected.append(conn_id)
                else:
                    disconnected.append(conn_id)
            
            # Clean up disconnected connections
            for conn_id in disconnected:
                if conn_id in self.connections:
                    del self.connections[conn_id]
    
    async def apply_edit(self, message: WebSocketMessage) -> bool:
        """Apply an edit operation to the session content."""
        async with self.lock:
            try:
                operation = message.data.get("operation", {})
                op_type = operation.get("type")
                
                if op_type == "insert":
                    position = operation.get("position", 0)
                    content = operation.get("content", "")
                    self.content = self.content[:position] + content + self.content[position:]
                
                elif op_type == "delete":
                    position = operation.get("position", 0)
                    length = operation.get("length", 0)
                    self.content = self.content[:position] + self.content[position + length:]
                
                self.version += 1
                self.edit_history.append(message)
                self.updated_at = datetime.utcnow()
                return True
            
            except Exception as e:
                logger.error(f"Failed to apply edit: {e}")
                return False
    
    async def add_comment(self, message: WebSocketMessage) -> bool:
        """Add a comment to the session."""
        async with self.lock:
            try:
                comment = {
                    "id": str(uuid4()),
                    "user_id": message.user_id,
                    "line": message.data.get("line", 0),
                    "text": message.data.get("text", ""),
                    "resolved": False,
                    "created_at": datetime.utcnow().isoformat(),
                    "replies": []
                }
                self.comments.append(comment)
                self.updated_at = datetime.utcnow()
                return True
            
            except Exception as e:
                logger.error(f"Failed to add comment: {e}")
                return False
    
    def get_participant_count(self) -> int:
        """Get the number of active participants."""
        return sum(1 for conn in self.connections.values() if conn.is_active())
    
    def get_participants(self) -> List[Dict[str, Any]]:
        """Get list of active participants."""
        participants = []
        for connection in self.connections.values():
            if connection.is_active():
                participants.append({
                    "user_id": connection.user_id,
                    "name": connection.user_info.get("name", "Unknown"),
                    "color": connection.user_info.get("color", "#000000"),
                    "cursor": connection.cursor_position,
                    "selection": connection.selection
                })
        return participants


class WebSocketConnectionManager:
    """Manages all WebSocket connections and collaboration sessions."""
    
    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
        self.user_connections: Dict[str, List[UserConnection]] = {}
        self.lock = asyncio.Lock()
        self.heartbeat_interval = 30  # seconds
        self.connection_timeout = 300  # seconds (5 minutes)
        
    async def create_session(
        self,
        session_id: str,
        owner_id: str,
        name: str = ""
    ) -> CollaborationSession:
        """Create a new collaboration session."""
        async with self.lock:
            session = CollaborationSession(session_id, owner_id, name)
            self.sessions[session_id] = session
            logger.info(f"Session {session_id} created by {owner_id}")
            return session
    
    async def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get a collaboration session."""
        return self.sessions.get(session_id)
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete a collaboration session."""
        async with self.lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                # Close all connections in the session
                for connection in session.connections.values():
                    await connection.close()
                del self.sessions[session_id]
                logger.info(f"Session {session_id} deleted")
                return True
            return False
    
    async def connect(
        self,
        websocket: WebSocket,
        session_id: str,
        user_id: str
    ) -> Optional[UserConnection]:
        """Connect a user to a session."""
        try:
            await websocket.accept()
            
            # Get or create session
            session = await self.get_session(session_id)
            if not session:
                session = await self.create_session(session_id, user_id)
            
            # Create connection
            connection = UserConnection(websocket, user_id, session_id)
            
            # Add to session
            success = await session.add_connection(connection)
            if not success:
                await connection.close()
                return None
            
            # Track user connections
            if user_id not in self.user_connections:
                self.user_connections[user_id] = []
            self.user_connections[user_id].append(connection)
            
            logger.info(f"User {user_id} connected to session {session_id}")
            return connection
        
        except Exception as e:
            logger.error(f"Failed to connect user {user_id}: {e}")
            return None
    
    async def disconnect(self, connection: UserConnection) -> None:
        """Disconnect a user from a session."""
        try:
            session = await self.get_session(connection.session_id)
            if session:
                await session.remove_connection(connection.connection_id)
            
            # Remove from user connections
            if connection.user_id in self.user_connections:
                self.user_connections[connection.user_id] = [
                    c for c in self.user_connections[connection.user_id]
                    if c.connection_id != connection.connection_id
                ]
            
            await connection.close()
            logger.info(f"User {connection.user_id} disconnected from session {connection.session_id}")
        
        except Exception as e:
            logger.error(f"Failed to disconnect user: {e}")
    
    async def broadcast_to_session(
        self,
        session_id: str,
        message: WebSocketMessage,
        exclude_connection_id: Optional[str] = None
    ) -> None:
        """Broadcast a message to all users in a session."""
        session = await self.get_session(session_id)
        if session:
            await session.broadcast_message(message, exclude_connection_id)
    
    async def send_to_user(
        self,
        user_id: str,
        message: WebSocketMessage
    ) -> None:
        """Send a message to all connections of a specific user."""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                if connection.is_active():
                    await connection.send_message(message)
    
    async def cleanup_inactive_connections(self) -> None:
        """Remove inactive connections from all sessions."""
        async with self.lock:
            for session in self.sessions.values():
                inactive = [
                    conn_id for conn_id, conn in session.connections.items()
                    if not conn.is_active(self.connection_timeout)
                ]
                
                for conn_id in inactive:
                    await session.remove_connection(conn_id)
                    logger.info(f"Removed inactive connection {conn_id}")
    
    async def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session."""
        session = await self.get_session(session_id)
        if not session:
            return {}
        
        return {
            "session_id": session_id,
            "participant_count": session.get_participant_count(),
            "participants": session.get_participants(),
            "edit_count": len(session.edit_history),
            "comment_count": len(session.comments),
            "version": session.version,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions."""
        return [
            {
                "session_id": session.session_id,
                "name": session.name,
                "owner_id": session.owner_id,
                "participant_count": session.get_participant_count(),
                "created_at": session.created_at.isoformat()
            }
            for session in self.sessions.values()
        ]


# Global connection manager instance
connection_manager = WebSocketConnectionManager()
