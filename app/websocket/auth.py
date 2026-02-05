"""
WebSocket Authentication and Authorization.

Handles JWT token validation, session authentication, and permission checks for WebSocket connections.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt

from app.config import get_settings
from app.security.auth import verify_token

logger = logging.getLogger(__name__)
settings = get_settings()


class WebSocketAuth:
    """WebSocket authentication handler."""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.user_connections: Dict[str, list] = {}
    
    async def authenticate_connection(
        self,
        token: Optional[str],
        session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate a WebSocket connection.
        
        Validates JWT token and checks session permissions.
        Returns user info if valid, None otherwise.
        """
        if not token:
            logger.warning(f"WebSocket connection attempt without token for session {session_id}")
            return None
        
        try:
            # Verify JWT token
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=["HS256"]
            )
            
            user_id = payload.get("sub")
            if not user_id:
                logger.warning("JWT token missing user ID")
                return None
            
            # Check session permissions
            session_info = await self.get_session_info(session_id)
            if not session_info:
                logger.warning(f"Session {session_id} not found")
                return None
            
            # Check if user has access to session
            if not await self.check_session_access(user_id, session_id):
                logger.warning(f"User {user_id} does not have access to session {session_id}")
                return None
            
            user_info = {
                "user_id": user_id,
                "session_id": session_id,
                "authenticated_at": datetime.utcnow().isoformat(),
                "token_expires_at": payload.get("exp")
            }
            
            # Track active session
            await self.register_connection(user_id, session_id, user_info)
            
            logger.info(f"User {user_id} authenticated for session {session_id}")
            return user_info
        
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information."""
        # Mock implementation - in production, query database
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Default session info
        return {
            "session_id": session_id,
            "name": f"Session {session_id}",
            "owner_id": "owner-1",
            "created_at": datetime.utcnow().isoformat(),
            "participants": []
        }
    
    async def check_session_access(
        self,
        user_id: str,
        session_id: str
    ) -> bool:
        """
        Check if user has access to session.
        
        Returns True if user is owner, participant, or has public access.
        """
        # Mock implementation - in production, check permissions in database
        session_info = await self.get_session_info(session_id)
        if not session_info:
            return False
        
        # Owner always has access
        if session_info.get("owner_id") == user_id:
            return True
        
        # Check if user is participant
        participants = session_info.get("participants", [])
        if user_id in participants:
            return True
        
        # Check if session is public
        if session_info.get("is_public", False):
            return True
        
        return False
    
    async def register_connection(
        self,
        user_id: str,
        session_id: str,
        user_info: Dict[str, Any]
    ):
        """Register an active WebSocket connection."""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = await self.get_session_info(session_id)
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = []
        
        self.user_connections[user_id].append({
            "session_id": session_id,
            "connected_at": datetime.utcnow().isoformat(),
            "info": user_info
        })
    
    async def unregister_connection(
        self,
        user_id: str,
        session_id: str
    ):
        """Unregister a WebSocket connection."""
        if user_id in self.user_connections:
            self.user_connections[user_id] = [
                conn for conn in self.user_connections[user_id]
                if conn["session_id"] != session_id
            ]
            
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
    
    async def get_session_participants(
        self,
        session_id: str
    ) -> list:
        """Get all connected participants in a session."""
        participants = []
        
        for user_id, connections in self.user_connections.items():
            for conn in connections:
                if conn["session_id"] == session_id:
                    participants.append({
                        "user_id": user_id,
                        "connected_at": conn["connected_at"]
                    })
        
        return participants
    
    async def check_permission(
        self,
        user_id: str,
        session_id: str,
        action: str
    ) -> bool:
        """
        Check if user has permission to perform an action in session.
        
        Actions: read, write, comment, delete, manage
        """
        # Mock implementation - in production, check role-based permissions
        session_info = await self.get_session_info(session_id)
        if not session_info:
            return False
        
        # Owner can do anything
        if session_info.get("owner_id") == user_id:
            return True
        
        # Participants can read and write
        if user_id in session_info.get("participants", []):
            if action in ["read", "write", "comment"]:
                return True
        
        # Public sessions allow read-only
        if session_info.get("is_public", False) and action == "read":
            return True
        
        return False
    
    async def revoke_token(self, token: str):
        """
        Revoke a token (add to blacklist).
        
        In production, store in Redis or database.
        """
        # Mock implementation
        logger.info(f"Token revoked: {token[:20]}...")
    
    async def is_token_revoked(self, token: str) -> bool:
        """Check if a token has been revoked."""
        # Mock implementation
        return False


# Global WebSocket auth instance
ws_auth = WebSocketAuth()
