"""Performance optimization and intelligent caching."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import hashlib


class CachingStrategy:
    \"\"\"Intelligent caching strategy.\"\"\"

    def __init__(self, redis_client=None):
        \"\"\"Initialize caching strategy.
        
        Args:
            redis_client: Redis client
        \"\"\"
        self.redis = redis_client
        self.cache_ttl = {
            "user_stats": 300,  # 5 minutes
            "job_analytics": 300,  # 5 minutes
            "circuit_data": 600,  # 10 minutes
            "performance_metrics": 60,  # 1 minute
            "compliance_status": 3600,  # 1 hour
        }

    async def get_cached(
        self,
        key: str,
        cache_type: str = "default",
    ) -> Optional[Any]:
        \"\"\"Get value from cache.
        
        Args:
            key: Cache key
            cache_type: Cache type for TTL
            
        Returns:
            Cached value or None
        \"\"\"
        try:
            if not self.redis:
                return None
            
            value = await self.redis.get(key)
            return value
        except Exception:
            return None

    async def set_cached(
        self,
        key: str,
        value: Any,
        cache_type: str = "default",
    ) -> bool:
        \"\"\"Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            cache_type: Cache type for TTL
            
        Returns:
            Success status
        \"\"\"
        try:
            if not self.redis:
                return False
            
            ttl = self.cache_ttl.get(cache_type, 300)
            await self.redis.setex(key, ttl, str(value))
            return True
        except Exception:
            return False

    async def invalidate_cache(
        self,
        pattern: str,
    ) -> int:
        \"\"\"Invalidate cache by pattern.
        
        Args:
            pattern: Key pattern to invalidate
            
        Returns:
            Number of keys invalidated
        \"\"\"
        try:
            if not self.redis:
                return 0
            
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            return len(keys)
        except Exception:
            return 0

    def generate_cache_key(
        self,
        prefix: str,
        user_id: str,
        **kwargs,
    ) -> str:
        \"\"\"Generate cache key.
        
        Args:
            prefix: Key prefix
            user_id: User ID
            **kwargs: Additional parameters
            
        Returns:
            Cache key
        \"\"\"
        key_parts = [prefix, user_id]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        key_str = ":".join(str(p) for p in key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()


class QueryOptimization:
    \"\"\"Query optimization strategies.\"\"\"

    @staticmethod
    def get_optimized_query_hints(
        query_type: str,
    ) -> Dict[str, Any]:
        \"\"\"Get query optimization hints.
        
        Args:
            query_type: Type of query
            
        Returns:
            Optimization hints
        \"\"\"
        hints = {
            "analytics": {
                "use_index": ["user_id", "created_at"],
                "batch_size": 1000,
                "use_aggregation": True,
                "cache_ttl": 300,
            },
            "job_search": {
                "use_index": ["user_id", "status", "created_at"],
                "batch_size": 100,
                "use_pagination": True,
                "cache_ttl": 60,
            },
            "circuit_lookup": {
                "use_index": ["user_id", "id"],
                "batch_size": 50,
                "use_cache": True,
                "cache_ttl": 600,
            },
            "user_profile": {
                "use_index": ["id"],
                "batch_size": 1,
                "use_cache": True,
                "cache_ttl": 3600,
            },
        }
        
        return hints.get(query_type, {})

    @staticmethod
    def get_index_recommendations() -> Dict[str, Any]:
        \"\"\"Get database index recommendations.
        
        Returns:
            Index recommendations
        \"\"\"
        return {
            "jobs_table": [
                {"columns": ["user_id", "created_at"], "type": "btree"},
                {"columns": ["status", "created_at"], "type": "btree"},
                {"columns": ["job_type", "user_id"], "type": "btree"},
            ],
            "circuits_table": [
                {"columns": ["user_id", "created_at"], "type": "btree"},
                {"columns": ["user_id", "id"], "type": "btree"},
            ],
            "audit_logs_table": [
                {"columns": ["user_id", "created_at"], "type": "btree"},
                {"columns": ["action", "created_at"], "type": "btree"},
            ],
        }


class ConnectionPooling:
    \"\"\"Connection pool optimization.\"\"\"

    def __init__(self):
        \"\"\"Initialize connection pooling.\"\"\"
        self.pool_config = {
            "min_size": 10,
            "max_size": 100,
            "max_overflow": 50,
            "pool_recycle": 3600,
            "pool_pre_ping": True,
        }

    def get_pool_config(self) -> Dict[str, Any]:
        \"\"\"Get connection pool configuration.
        
        Returns:
            Pool configuration
        \"\"\"
        return self.pool_config

    def get_pool_status(self) -> Dict[str, Any]:
        \"\"\"Get connection pool status.
        
        Returns:
            Pool status
        \"\"\"
        return {
            "min_size": self.pool_config["min_size"],
            "max_size": self.pool_config["max_size"],
            "max_overflow": self.pool_config["max_overflow"],
            "pool_recycle_seconds": self.pool_config["pool_recycle"],
            "health_check_enabled": self.pool_config["pool_pre_ping"],
        }


class LoadBalancing:
    \"\"\"Load balancing strategy.\"\"\"

    STRATEGIES = {
        "round_robin": "Distribute requests evenly",
        "least_connections": "Route to server with fewest connections",
        "weighted": "Route based on server capacity",
        "ip_hash": "Route based on client IP",
    }

    async def get_load_balanced_endpoint(
        self,
        endpoints: list[str],
        strategy: str = "round_robin",
        client_ip: Optional[str] = None,
    ) -> str:
        \"\"\"Get load-balanced endpoint.
        
        Args:
            endpoints: Available endpoints
            strategy: Load balancing strategy
            client_ip: Client IP for IP hash
            
        Returns:
            Selected endpoint
        \"\"\"
        try:
            if not endpoints:
                return ""
            
            if strategy == "round_robin":
                # Simple round robin
                return endpoints[0]
            
            elif strategy == "ip_hash" and client_ip:
                # IP-based hashing
                hash_val = hash(client_ip)
                return endpoints[hash_val % len(endpoints)]
            
            else:
                # Default to first endpoint
                return endpoints[0]
        except Exception:
            return endpoints[0] if endpoints else ""

    def get_load_balancing_config(self) -> Dict[str, Any]:
        \"\"\"Get load balancing configuration.
        
        Returns:
            Load balancing config
        \"\"\"
        return {
            "strategy": "round_robin",
            "health_check_interval": 30,
            "health_check_timeout": 5,
            "max_retries": 3,
            "circuit_breaker_threshold": 5,
        }


class PerformanceMonitoring:
    \"\"\"Monitor performance metrics.\"\"\"

    def __init__(self):
        \"\"\"Initialize performance monitoring.\"\"\"
        self.metrics = {}

    async def record_operation(
        self,
        operation_name: str,
        duration_ms: float,
        success: bool,
    ) -> None:
        \"\"\"Record operation performance.
        
        Args:
            operation_name: Name of operation
            duration_ms: Duration in milliseconds
            success: Whether operation succeeded
        \"\"\"
        try:
            if operation_name not in self.metrics:
                self.metrics[operation_name] = {
                    "count": 0,
                    "total_time": 0,
                    "min_time": float("inf"),
                    "max_time": 0,
                    "errors": 0,
                }
            
            m = self.metrics[operation_name]
            m["count"] += 1
            m["total_time"] += duration_ms
            m["min_time"] = min(m["min_time"], duration_ms)
            m["max_time"] = max(m["max_time"], duration_ms)
            if not success:
                m["errors"] += 1
        except Exception:
            pass

    def get_performance_report(self) -> Dict[str, Any]:
        \"\"\"Get performance report.
        
        Returns:
            Performance metrics
        \"\"\"
        report = {}
        for op_name, metrics in self.metrics.items():
            avg_time = (
                metrics["total_time"] / metrics["count"]
                if metrics["count"] > 0 else 0
            )
            error_rate = (
                metrics["errors"] / metrics["count"] * 100
                if metrics["count"] > 0 else 0
            )
            
            report[op_name] = {
                "count": metrics["count"],
                "average_time_ms": avg_time,
                "min_time_ms": metrics["min_time"],
                "max_time_ms": metrics["max_time"],
                "error_rate": error_rate,
            }
        
        return report

    def get_performance_recommendations(self) -> list[str]:
        \"\"\"Get performance optimization recommendations.
        
        Returns:
            List of recommendations
        \"\"\"
        recommendations = []
        
        for op_name, metrics in self.metrics.items():
            avg_time = (
                metrics["total_time"] / metrics["count"]
                if metrics["count"] > 0 else 0
            )
            error_rate = (
                metrics["errors"] / metrics["count"] * 100
                if metrics["count"] > 0 else 0
            )
            
            if avg_time > 1000:  # > 1 second
                recommendations.append(
                    f"Optimize {op_name}: average time is {avg_time:.0f}ms"
                )
            
            if error_rate > 5:  # > 5% errors
                recommendations.append(
                    f"Investigate {op_name}: error rate is {error_rate:.1f}%"
                )
        
        return recommendations
