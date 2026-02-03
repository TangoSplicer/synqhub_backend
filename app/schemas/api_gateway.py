"""Pydantic schemas for API gateway endpoints."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from pydantic import BaseModel, Field


class APIRouteBase(BaseModel):
    \"\"\"Base schema for API routes.\"\"\"
    
    name: str = Field(..., min_length=1, max_length=255)
    path: str = Field(..., min_length=1, max_length=500)
    method: str = Field(..., pattern=\"^(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)$\")
    target_service: str = Field(..., min_length=1, max_length=100)
    target_path: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None


class APIRouteCreate(APIRouteBase):
    \"\"\"Schema for creating API routes.\"\"\"
    
    request_transformation: Optional[Dict[str, Any]] = None
    response_transformation: Optional[Dict[str, Any]] = None
    rate_limit_requests: Optional[int] = None
    rate_limit_window_seconds: Optional[int] = None
    requires_auth: bool = True
    required_scopes: Optional[List[str]] = None


class APIRouteUpdate(BaseModel):
    \"\"\"Schema for updating API routes.\"\"\"
    
    name: Optional[str] = None
    description: Optional[str] = None
    target_service: Optional[str] = None
    target_path: Optional[str] = None
    request_transformation: Optional[Dict[str, Any]] = None
    response_transformation: Optional[Dict[str, Any]] = None
    rate_limit_requests: Optional[int] = None
    rate_limit_window_seconds: Optional[int] = None
    requires_auth: Optional[bool] = None
    required_scopes: Optional[List[str]] = None
    is_active: Optional[bool] = None


class APIRouteResponse(APIRouteBase):
    \"\"\"Schema for API route responses.\"\"\"
    
    id: UUID
    request_transformation: Optional[Dict[str, Any]] = None
    response_transformation: Optional[Dict[str, Any]] = None
    rate_limit_requests: Optional[int] = None
    rate_limit_window_seconds: Optional[int] = None
    requires_auth: bool
    required_scopes: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class APIRequestBase(BaseModel):
    \"\"\"Base schema for API requests.\"\"\"
    
    method: str = Field(..., pattern=\"^(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)$\")
    path: str = Field(..., min_length=1, max_length=500)
    status_code: int = Field(..., ge=100, le=599)
    response_time_ms: float = Field(..., ge=0.0)


class APIRequestResponse(APIRequestBase):
    \"\"\"Schema for API request responses.\"\"\"
    
    id: UUID
    route_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    query_params: Optional[Dict[str, Any]] = None
    request_size_bytes: Optional[int] = None
    response_size_bytes: Optional[int] = None
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    timestamp: datetime
    user_agent: Optional[str] = None
    client_ip: Optional[str] = None
    
    class Config:
        from_attributes = True


class APIKeyBase(BaseModel):
    \"\"\"Base schema for API keys.\"\"\"
    
    name: str = Field(..., min_length=1, max_length=255)
    scopes: List[str]


class APIKeyCreate(APIKeyBase):
    \"\"\"Schema for creating API keys.\"\"\"
    
    rate_limit_requests: Optional[int] = None
    rate_limit_window_seconds: Optional[int] = None
    expires_at: Optional[datetime] = None


class APIKeyResponse(APIKeyBase):
    \"\"\"Schema for API key responses.\"\"\"
    
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    rate_limit_requests: Optional[int] = None
    rate_limit_window_seconds: Optional[int] = None
    
    class Config:
        from_attributes = True


class APIKeyCreateResponse(APIKeyResponse):
    \"\"\"Schema for API key creation response (includes the actual key).\"\"\"
    
    key: str  # Only returned on creation


class RateLimitQuotaBase(BaseModel):
    \"\"\"Base schema for rate limit quotas.\"\"\"
    
    requests_per_minute: int = Field(default=100, ge=1)
    requests_per_hour: int = Field(default=5000, ge=1)
    requests_per_day: int = Field(default=100000, ge=1)


class RateLimitQuotaCreate(RateLimitQuotaBase):
    \"\"\"Schema for creating rate limit quotas.\"\"\"
    
    user_id: Optional[UUID] = None
    api_key_id: Optional[UUID] = None


class RateLimitQuotaResponse(RateLimitQuotaBase):
    \"\"\"Schema for rate limit quota responses.\"\"\"
    
    id: UUID
    user_id: Optional[UUID] = None
    api_key_id: Optional[UUID] = None
    requests_this_minute: int
    requests_this_hour: int
    requests_this_day: int
    is_blocked: bool
    blocked_until: Optional[datetime] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True


class APIAnalyticsBase(BaseModel):
    \"\"\"Base schema for API analytics.\"\"\"
    
    period_start: datetime
    period_end: datetime
    period_type: str = Field(..., pattern=\"^(hourly|daily|weekly|monthly)$\")


class APIAnalyticsResponse(APIAnalyticsBase):
    \"\"\"Schema for API analytics responses.\"\"\"
    
    id: UUID
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    error_rate: float
    top_errors: Dict[str, int]
    requests_by_route: Dict[str, int]
    requests_by_user: Dict[str, int]
    total_request_bytes: int
    total_response_bytes: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class GraphQLSchemaBase(BaseModel):
    \"\"\"Base schema for GraphQL schemas.\"\"\"
    
    name: str = Field(..., min_length=1, max_length=255)
    version: str = Field(..., min_length=1, max_length=50)
    schema_definition: str
    description: Optional[str] = None


class GraphQLSchemaCreate(GraphQLSchemaBase):
    \"\"\"Schema for creating GraphQL schemas.\"\"\"
    
    pass


class GraphQLSchemaResponse(GraphQLSchemaBase):
    \"\"\"Schema for GraphQL schema responses.\"\"\"
    
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class APIGatewayStatus(BaseModel):
    \"\"\"Schema for API gateway status.\"\"\"
    
    status: str = Field(..., pattern=\"^(healthy|degraded|unhealthy)$\")
    uptime_seconds: float
    total_requests: int
    requests_per_second: float
    active_connections: int
    average_response_time_ms: float
    error_rate: float


class APIUsageStats(BaseModel):
    \"\"\"Schema for API usage statistics.\"\"\"
    
    user_id: Optional[UUID] = None
    api_key_id: Optional[UUID] = None
    period: str = Field(..., pattern=\"^(today|this_week|this_month|all_time)$\")
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_bytes_sent: int
    total_bytes_received: int
    average_response_time_ms: float
    most_used_endpoints: List[Dict[str, Any]]
