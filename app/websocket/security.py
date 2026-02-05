"""
WebSocket Security and Rate Limiting.

Implements rate limiting, message validation, and security checks for WebSocket connections.
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for WebSocket messages."""
    
    def __init__(
        self,
        max_messages_per_second: int = 10,
        max_messages_per_minute: int = 500,
        max_message_size: int = 1024 * 100  # 100KB
    ):
        self.max_messages_per_second = max_messages_per_second
        self.max_messages_per_minute = max_messages_per_minute
        self.max_message_size = max_message_size
        
        self.message_counts: Dict[str, list] = defaultdict(list)
        self.user_limits: Dict[str, Dict[str, Any]] = {}
    
    async def check_rate_limit(
        self,
        user_id: str,
        session_id: str
    ) -> tuple[bool, Optional[str]]:
        """
        Check if user has exceeded rate limits.
        
        Returns (allowed, error_message)
        """
        key = f"{user_id}:{session_id}"
        now = datetime.utcnow()
        
        # Get message timestamps for this user
        if key not in self.message_counts:
            self.message_counts[key] = []
        
        timestamps = self.message_counts[key]
        
        # Remove old timestamps
        one_minute_ago = now - timedelta(minutes=1)
        timestamps = [ts for ts in timestamps if ts > one_minute_ago]
        self.message_counts[key] = timestamps
        
        # Check per-minute limit
        if len(timestamps) >= self.max_messages_per_minute:
            return False, "Rate limit exceeded (per minute)"
        
        # Check per-second limit
        one_second_ago = now - timedelta(seconds=1)
        recent_messages = len([ts for ts in timestamps if ts > one_second_ago])
        
        if recent_messages >= self.max_messages_per_second:
            return False, "Rate limit exceeded (per second)"
        
        # Record this message
        timestamps.append(now)
        self.message_counts[key] = timestamps
        
        return True, None
    
    async def check_message_size(self, message: str) -> tuple[bool, Optional[str]]:
        """Check if message size is within limits."""
        if len(message.encode('utf-8')) > self.max_message_size:
            return False, f"Message exceeds maximum size of {self.max_message_size} bytes"
        
        return True, None
    
    async def get_user_limits(self, user_id: str) -> Dict[str, Any]:
        """Get rate limit info for a user."""
        return self.user_limits.get(user_id, {
            "messages_per_second": self.max_messages_per_second,
            "messages_per_minute": self.max_messages_per_minute,
            "max_message_size": self.max_message_size
        })


class MessageValidator:
    """Validates WebSocket messages."""
    
    VALID_MESSAGE_TYPES = {
        "edit",
        "presence",
        "comment",
        "undo",
        "redo",
        "sync",
        "ping",
        "subscribe",
        "unsubscribe"
    }
    
    REQUIRED_FIELDS = {
        "edit": ["type", "content", "position"],
        "presence": ["type", "cursor", "selection"],
        "comment": ["type", "line", "text"],
        "undo": ["type"],
        "redo": ["type"],
        "sync": ["type"],
        "ping": ["type"],
        "subscribe": ["type", "channel"],
        "unsubscribe": ["type", "channel"]
    }
    
    async def validate_message(
        self,
        message: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a WebSocket message.
        
        Returns (valid, error_message)
        """
        if not isinstance(message, dict):
            return False, "Message must be a dictionary"
        
        msg_type = message.get("type")
        if not msg_type:
            return False, "Message type is required"
        
        if msg_type not in self.VALID_MESSAGE_TYPES:
            return False, f"Invalid message type: {msg_type}"
        
        # Check required fields
        required = self.REQUIRED_FIELDS.get(msg_type, [])
        for field in required:
            if field not in message:
                return False, f"Missing required field: {field}"
        
        # Type-specific validation
        if msg_type == "edit":
            valid, error = await self._validate_edit(message)
            if not valid:
                return False, error
        
        elif msg_type == "comment":
            valid, error = await self._validate_comment(message)
            if not valid:
                return False, error
        
        elif msg_type == "presence":
            valid, error = await self._validate_presence(message)
            if not valid:
                return False, error
        
        return True, None
    
    async def _validate_edit(self, message: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate edit message."""
        content = message.get("content")
        if not isinstance(content, str):
            return False, "Edit content must be a string"
        
        if len(content) > 10000:
            return False, "Edit content too large (max 10000 chars)"
        
        position = message.get("position")
        if not isinstance(position, dict):
            return False, "Position must be an object"
        
        if "line" not in position or "column" not in position:
            return False, "Position must have line and column"
        
        return True, None
    
    async def _validate_comment(self, message: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate comment message."""
        text = message.get("text")
        if not isinstance(text, str):
            return False, "Comment text must be a string"
        
        if len(text) > 5000:
            return False, "Comment text too large (max 5000 chars)"
        
        line = message.get("line")
        if not isinstance(line, int) or line < 0:
            return False, "Line must be a non-negative integer"
        
        return True, None
    
    async def _validate_presence(self, message: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate presence message."""
        cursor = message.get("cursor")
        if cursor and not isinstance(cursor, dict):
            return False, "Cursor must be an object"
        
        selection = message.get("selection")
        if selection and not isinstance(selection, dict):
            return False, "Selection must be an object"
        
        return True, None


class SecurityChecker:
    """Security checks for WebSocket connections."""
    
    def __init__(self):
        self.blocked_users: set = set()
        self.suspicious_activity: Dict[str, list] = defaultdict(list)
    
    async def check_injection_attack(self, message: str) -> bool:
        """Check for potential injection attacks."""
        dangerous_patterns = [
            "javascript:",
            "<script",
            "onclick=",
            "onerror=",
            "eval(",
            "exec(",
            "__import__"
        ]
        
        message_lower = message.lower()
        for pattern in dangerous_patterns:
            if pattern in message_lower:
                logger.warning(f"Potential injection attack detected: {pattern}")
                return False
        
        return True
    
    async def check_xss_attack(self, message: str) -> bool:
        """Check for potential XSS attacks."""
        xss_patterns = [
            r"<\s*script",
            r"javascript:",
            r"on\w+\s*=",
            r"<\s*iframe",
            r"<\s*object",
            r"<\s*embed"
        ]
        
        import re
        for pattern in xss_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                logger.warning(f"Potential XSS attack detected: {pattern}")
                return False
        
        return True
    
    async def check_dos_attack(
        self,
        user_id: str,
        message_size: int
    ) -> bool:
        """Check for potential DoS attacks."""
        # Track message sizes per user
        if user_id not in self.suspicious_activity:
            self.suspicious_activity[user_id] = []
        
        activity = self.suspicious_activity[user_id]
        now = datetime.utcnow()
        
        # Remove old entries (older than 1 minute)
        activity = [
            (ts, size) for ts, size in activity
            if now - ts < timedelta(minutes=1)
        ]
        
        # Check for large messages
        if message_size > 1024 * 50:  # 50KB
            activity.append((now, message_size))
            
            # If more than 5 large messages in a minute, flag as suspicious
            if len(activity) > 5:
                logger.warning(f"Potential DoS attack from user {user_id}")
                return False
        
        self.suspicious_activity[user_id] = activity
        return True
    
    async def block_user(self, user_id: str):
        """Block a user from WebSocket connections."""
        self.blocked_users.add(user_id)
        logger.warning(f"User {user_id} blocked from WebSocket connections")
    
    async def unblock_user(self, user_id: str):
        """Unblock a user."""
        self.blocked_users.discard(user_id)
    
    async def is_user_blocked(self, user_id: str) -> bool:
        """Check if user is blocked."""
        return user_id in self.blocked_users


# Global instances
rate_limiter = RateLimiter()
message_validator = MessageValidator()
security_checker = SecurityChecker()
