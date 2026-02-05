"""
WebSocket Message Handler for processing collaboration messages.

Handles different message types (edits, presence, comments, etc.)
and routes them appropriately.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from uuid import uuid4

from app.websocket.connection_manager import (
    WebSocketMessage,
    MessageType,
    UserConnection,
    CollaborationSession
)

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles WebSocket messages."""
    
    def __init__(self):
        self.handlers: Dict[MessageType, Callable] = {
            MessageType.EDIT: self.handle_edit,
            MessageType.PRESENCE: self.handle_presence,
            MessageType.COMMENT: self.handle_comment,
            MessageType.UNDO: self.handle_undo,
            MessageType.REDO: self.handle_redo,
            MessageType.SYNC: self.handle_sync,
            MessageType.HEARTBEAT: self.handle_heartbeat,
        }
    
    async def process_message(
        self,
        message: WebSocketMessage,
        connection: UserConnection,
        session: CollaborationSession
    ) -> bool:
        """Process an incoming message."""
        try:
            handler = self.handlers.get(message.type)
            if handler:
                return await handler(message, connection, session)
            else:
                logger.warning(f"Unknown message type: {message.type}")
                return False
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return False
    
    async def handle_edit(
        self,
        message: WebSocketMessage,
        connection: UserConnection,
        session: CollaborationSession
    ) -> bool:
        """Handle edit operations (insert, delete, transform)."""
        try:
            operation = message.data.get("operation", {})
            
            # Apply edit to session
            success = await session.apply_edit(message)
            if not success:
                return False
            
            # Send acknowledgment
            ack_message = WebSocketMessage(
                type=MessageType.ACK,
                session_id=message.session_id,
                user_id=message.user_id,
                timestamp=datetime.utcnow(),
                data={"operation_id": message.operation_id},
                version=session.version
            )
            await connection.send_message(ack_message)
            
            # Broadcast to other users
            broadcast_message = WebSocketMessage(
                type=MessageType.EDIT,
                session_id=message.session_id,
                user_id=message.user_id,
                timestamp=datetime.utcnow(),
                data=operation,
                version=session.version,
                operation_id=message.operation_id
            )
            await session.broadcast_message(broadcast_message, connection.connection_id)
            
            logger.info(f"Edit applied: {operation.get('type')} by {message.user_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error handling edit: {e}")
            return False
    
    async def handle_presence(
        self,
        message: WebSocketMessage,
        connection: UserConnection,
        session: CollaborationSession
    ) -> bool:
        """Handle presence updates (cursor, selection, user info)."""
        try:
            presence_type = message.data.get("presence_type")
            
            if presence_type == "cursor":
                connection.cursor_position = {
                    "line": message.data.get("line", 0),
                    "column": message.data.get("column", 0)
                }
            
            elif presence_type == "selection":
                connection.selection = {
                    "start": message.data.get("start", 0),
                    "end": message.data.get("end", 0)
                }
            
            elif presence_type == "user_info":
                connection.user_info = {
                    "name": message.data.get("name", "Unknown"),
                    "color": message.data.get("color", "#000000")
                }
            
            # Broadcast presence update
            broadcast_message = WebSocketMessage(
                type=MessageType.PRESENCE,
                session_id=message.session_id,
                user_id=message.user_id,
                timestamp=datetime.utcnow(),
                data={
                    "presence_type": presence_type,
                    "user_id": message.user_id,
                    "cursor": connection.cursor_position,
                    "selection": connection.selection,
                    "user_info": connection.user_info
                },
                version=session.version
            )
            await session.broadcast_message(broadcast_message, connection.connection_id)
            
            return True
        
        except Exception as e:
            logger.error(f"Error handling presence: {e}")
            return False
    
    async def handle_comment(
        self,
        message: WebSocketMessage,
        connection: UserConnection,
        session: CollaborationSession
    ) -> bool:
        """Handle comment operations (add, reply, resolve)."""
        try:
            comment_type = message.data.get("comment_type")
            
            if comment_type == "add":
                success = await session.add_comment(message)
                if not success:
                    return False
                
                # Broadcast new comment
                broadcast_message = WebSocketMessage(
                    type=MessageType.COMMENT,
                    session_id=message.session_id,
                    user_id=message.user_id,
                    timestamp=datetime.utcnow(),
                    data={
                        "comment_type": "add",
                        "line": message.data.get("line", 0),
                        "text": message.data.get("text", ""),
                        "user_name": connection.user_info.get("name", "Unknown")
                    },
                    version=session.version
                )
                await session.broadcast_message(broadcast_message)
            
            elif comment_type == "reply":
                # Handle comment reply
                comment_id = message.data.get("comment_id")
                reply_text = message.data.get("text", "")
                
                # Find and update comment
                for comment in session.comments:
                    if comment["id"] == comment_id:
                        comment["replies"].append({
                            "id": str(uuid4()),
                            "user_id": message.user_id,
                            "text": reply_text,
                            "created_at": datetime.utcnow().isoformat()
                        })
                        break
                
                # Broadcast reply
                broadcast_message = WebSocketMessage(
                    type=MessageType.COMMENT,
                    session_id=message.session_id,
                    user_id=message.user_id,
                    timestamp=datetime.utcnow(),
                    data={
                        "comment_type": "reply",
                        "comment_id": comment_id,
                        "text": reply_text,
                        "user_name": connection.user_info.get("name", "Unknown")
                    },
                    version=session.version
                )
                await session.broadcast_message(broadcast_message)
            
            elif comment_type == "resolve":
                # Mark comment as resolved
                comment_id = message.data.get("comment_id")
                for comment in session.comments:
                    if comment["id"] == comment_id:
                        comment["resolved"] = True
                        break
                
                # Broadcast resolution
                broadcast_message = WebSocketMessage(
                    type=MessageType.COMMENT,
                    session_id=message.session_id,
                    user_id=message.user_id,
                    timestamp=datetime.utcnow(),
                    data={
                        "comment_type": "resolve",
                        "comment_id": comment_id
                    },
                    version=session.version
                )
                await session.broadcast_message(broadcast_message)
            
            return True
        
        except Exception as e:
            logger.error(f"Error handling comment: {e}")
            return False
    
    async def handle_undo(
        self,
        message: WebSocketMessage,
        connection: UserConnection,
        session: CollaborationSession
    ) -> bool:
        """Handle undo operations."""
        try:
            if len(session.edit_history) > 0:
                # Get last edit
                last_edit = session.edit_history[-1]
                
                # Reverse the operation
                operation = last_edit.data.get("operation", {})
                op_type = operation.get("type")
                
                if op_type == "insert":
                    # Reverse insert by deleting
                    position = operation.get("position", 0)
                    length = len(operation.get("content", ""))
                    session.content = session.content[:position] + session.content[position + length:]
                
                elif op_type == "delete":
                    # Reverse delete by inserting
                    position = operation.get("position", 0)
                    content = operation.get("content", "")
                    session.content = session.content[:position] + content + session.content[position:]
                
                session.version += 1
                session.edit_history.pop()
                
                # Broadcast undo
                broadcast_message = WebSocketMessage(
                    type=MessageType.UNDO,
                    session_id=message.session_id,
                    user_id=message.user_id,
                    timestamp=datetime.utcnow(),
                    data={"operation": operation},
                    version=session.version
                )
                await session.broadcast_message(broadcast_message)
                
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error handling undo: {e}")
            return False
    
    async def handle_redo(
        self,
        message: WebSocketMessage,
        connection: UserConnection,
        session: CollaborationSession
    ) -> bool:
        """Handle redo operations."""
        try:
            # For now, redo is handled by the client
            # This is a placeholder for server-side redo support
            
            broadcast_message = WebSocketMessage(
                type=MessageType.REDO,
                session_id=message.session_id,
                user_id=message.user_id,
                timestamp=datetime.utcnow(),
                data=message.data,
                version=session.version
            )
            await session.broadcast_message(broadcast_message)
            
            return True
        
        except Exception as e:
            logger.error(f"Error handling redo: {e}")
            return False
    
    async def handle_sync(
        self,
        message: WebSocketMessage,
        connection: UserConnection,
        session: CollaborationSession
    ) -> bool:
        """Handle full synchronization requests."""
        try:
            # Send full state to requesting client
            sync_message = WebSocketMessage(
                type=MessageType.SYNC,
                session_id=message.session_id,
                user_id=message.user_id,
                timestamp=datetime.utcnow(),
                data={
                    "content": session.content,
                    "version": session.version,
                    "participants": session.get_participants(),
                    "comments": session.comments,
                    "edit_count": len(session.edit_history)
                },
                version=session.version
            )
            await connection.send_message(sync_message)
            
            return True
        
        except Exception as e:
            logger.error(f"Error handling sync: {e}")
            return False
    
    async def handle_heartbeat(
        self,
        message: WebSocketMessage,
        connection: UserConnection,
        session: CollaborationSession
    ) -> bool:
        """Handle heartbeat/ping messages."""
        try:
            # Send heartbeat response
            heartbeat_message = WebSocketMessage(
                type=MessageType.HEARTBEAT,
                session_id=message.session_id,
                user_id=message.user_id,
                timestamp=datetime.utcnow(),
                data={"status": "alive"},
                version=session.version
            )
            await connection.send_message(heartbeat_message)
            
            return True
        
        except Exception as e:
            logger.error(f"Error handling heartbeat: {e}")
            return False


# Global message handler instance
message_handler = MessageHandler()
