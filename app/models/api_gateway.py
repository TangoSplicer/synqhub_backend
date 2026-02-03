"""API Gateway models for Phase 6 enhanced routing and analytics."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer, Float, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from app.database import Base


class APIRoute(Base):
    """Represents a custom API route configuration."""
    
    __tablename__ = "api_routes"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    path = Column(String(500), nullable=False, unique=True)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE, etc.
    
    # Route configuration
    description = Column(Text, nullable=True)
    target_service = Column(String(100), nullable=False)  # Which backend service to route to
    target_path = Column(String(500), nullable=False)
    
    # Request/response transformation
    request_transformation = Column(JSON, nullable=True)  # Transformation rules
    response_transformation = Column(JSON, nullable=True)  # Transformation rules
    
    # Rate limiting
    rate_limit_requests = Column(Integer, nullable=True)
    rate_limit_window_seconds = Column(Integer, nullable=True)
    
    # Authentication
    requires_auth = Column(Boolean, default=True, nullable=False)
    required_scopes = Column(JSON, nullable=True)  # List of required OAuth scopes
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    requests = relationship("APIRequest", back_populates="route", cascade="all, delete-orphan")


class APIRequest(Base):
    """Tracks individual API requests for analytics."""
    
    __tablename__ = "api_requests"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    route_id = Column(PG_UUID(as_uuid=True), ForeignKey("api_routes.id"), nullable=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Request details
    method = Column(String(10), nullable=False)
    path = Column(String(500), nullable=False)
    query_params = Column(JSON, nullable=True)
    
    # Response details
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    
    # Size metrics
    request_size_bytes = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    error_type = Column(String(100), nullable=True)
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_agent = Column(String(500), nullable=True)
    client_ip = Column(String(50), nullable=True)
    
    # Relationships
    route = relationship("APIRoute", back_populates="requests")
    user = relationship("User")


class APIKey(Base):
    """Represents an API key for programmatic access."""
    
    __tablename__ = "api_keys"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Key details
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)
    
    # Permissions
    scopes = Column(JSON, nullable=False)  # List of allowed scopes
    
    # Rate limiting
    rate_limit_requests = Column(Integer, nullable=True)
    rate_limit_window_seconds = Column(Integer, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")


class RateLimitQuota(Base):
    """Tracks rate limit quotas for users and API keys."""
    
    __tablename__ = "rate_limit_quotas"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    api_key_id = Column(PG_UUID(as_uuid=True), ForeignKey("api_keys.id"), nullable=True)
    
    # Quota configuration
    requests_per_minute = Column(Integer, nullable=False, default=100)
    requests_per_hour = Column(Integer, nullable=False, default=5000)
    requests_per_day = Column(Integer, nullable=False, default=100000)
    
    # Current usage
    requests_this_minute = Column(Integer, default=0, nullable=False)
    requests_this_hour = Column(Integer, default=0, nullable=False)
    requests_this_day = Column(Integer, default=0, nullable=False)
    
    # Tracking
    minute_window_start = Column(DateTime, nullable=True)
    hour_window_start = Column(DateTime, nullable=True)
    day_window_start = Column(DateTime, nullable=True)
    
    # Status
    is_blocked = Column(Boolean, default=False, nullable=False)
    blocked_until = Column(DateTime, nullable=True)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class APIAnalytics(Base):
    """Aggregated analytics for API usage."""
    
    __tablename__ = "api_analytics"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    
    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)  # "hourly", "daily", "weekly", "monthly"
    
    # Metrics
    total_requests = Column(Integer, default=0, nullable=False)
    successful_requests = Column(Integer, default=0, nullable=False)
    failed_requests = Column(Integer, default=0, nullable=False)
    
    # Performance
    avg_response_time_ms = Column(Float, nullable=False)
    p50_response_time_ms = Column(Float, nullable=False)
    p95_response_time_ms = Column(Float, nullable=False)
    p99_response_time_ms = Column(Float, nullable=False)
    
    # Errors
    error_rate = Column(Float, nullable=False)
    top_errors = Column(JSON, nullable=False)  # Most common error types
    
    # Usage by route
    requests_by_route = Column(JSON, nullable=False)  # {route_id: count}
    requests_by_user = Column(JSON, nullable=False)  # {user_id: count}
    
    # Data transfer
    total_request_bytes = Column(Integer, default=0, nullable=False)
    total_response_bytes = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class GraphQLSchema(Base):
    """Represents GraphQL schema configuration."""
    
    __tablename__ = "graphql_schemas"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    version = Column(String(50), nullable=False)
    
    # Schema definition
    schema_definition = Column(Text, nullable=False)  # GraphQL SDL
    
    # Metadata
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
