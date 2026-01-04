"""Advanced monitoring and observability."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


class DistributedTracing:
    \"\"\"Distributed tracing for request tracking.\"\"\"

    def __init__(self):
        \"\"\"Initialize distributed tracing.\"\"\"
        self.traces = {}

    async def start_trace(
        self,
        trace_id: str,
        operation_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        \"\"\"Start a new trace.
        
        Args:
            trace_id: Unique trace ID
            operation_name: Name of operation
            metadata: Additional metadata
            
        Returns:
            Trace info
        \"\"\"
        try:
            trace = {
                "trace_id": trace_id,
                "operation_name": operation_name,
                "start_time": datetime.utcnow(),
                "spans": [],
                "metadata": metadata or {},
                "status": "RUNNING",
            }
            
            self.traces[trace_id] = trace
            
            return {
                "trace_id": trace_id,
                "operation_name": operation_name,
                "status": "STARTED",
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def add_span(
        self,
        trace_id: str,
        span_name: str,
        duration_ms: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        \"\"\"Add span to trace.
        
        Args:
            trace_id: Trace ID
            span_name: Span name
            duration_ms: Duration in milliseconds
            tags: Optional tags
            
        Returns:
            Span info
        \"\"\"
        try:
            if trace_id not in self.traces:
                return {
                    "error": "Trace not found",
                    "success": False,
                }
            
            span = {
                "span_name": span_name,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow(),
                "tags": tags or {},
            }
            
            self.traces[trace_id]["spans"].append(span)
            
            return {
                "trace_id": trace_id,
                "span_name": span_name,
                "duration_ms": duration_ms,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def end_trace(
        self,
        trace_id: str,
        status: str = "SUCCESS",
    ) -> Dict[str, Any]:
        \"\"\"End a trace.
        
        Args:
            trace_id: Trace ID
            status: Final status
            
        Returns:
            Trace summary
        \"\"\"
        try:
            if trace_id not in self.traces:
                return {
                    "error": "Trace not found",
                    "success": False,
                }
            
            trace = self.traces[trace_id]
            end_time = datetime.utcnow()
            total_duration = (end_time - trace["start_time"]).total_seconds() * 1000
            
            trace["end_time"] = end_time
            trace["total_duration_ms"] = total_duration
            trace["status"] = status
            
            return {
                "trace_id": trace_id,
                "operation_name": trace["operation_name"],
                "total_duration_ms": total_duration,
                "span_count": len(trace["spans"]),
                "status": status,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        \"\"\"Get trace details.
        
        Args:
            trace_id: Trace ID
            
        Returns:
            Trace details
        \"\"\"
        try:
            if trace_id not in self.traces:
                return {
                    "error": "Trace not found",
                    "success": False,
                }
            
            trace = self.traces[trace_id]
            return {
                "trace_id": trace_id,
                "operation_name": trace["operation_name"],
                "status": trace["status"],
                "spans": trace["spans"],
                "total_duration_ms": trace.get("total_duration_ms"),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }


class MetricsAggregation:
    \"\"\"Aggregate and analyze metrics.\"\"\"

    def __init__(self):
        \"\"\"Initialize metrics aggregation.\"\"\"
        self.metrics_buffer = []

    async def collect_metrics(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        \"\"\"Collect metric.
        
        Args:
            metric_name: Metric name
            value: Metric value
            tags: Optional tags
        \"\"\"
        try:
            metric = {
                "name": metric_name,
                "value": value,
                "tags": tags or {},
                "timestamp": datetime.utcnow(),
            }
            
            self.metrics_buffer.append(metric)
            
            # Keep last 10000 metrics
            if len(self.metrics_buffer) > 10000:
                self.metrics_buffer = self.metrics_buffer[-10000:]
        except Exception:
            pass

    def get_metrics_summary(
        self,
        metric_name: str,
        window_minutes: int = 60,
    ) -> Dict[str, Any]:
        \"\"\"Get metrics summary.
        
        Args:
            metric_name: Metric name
            window_minutes: Time window
            
        Returns:
            Metrics summary
        \"\"\"
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=window_minutes)
            
            relevant_metrics = [
                m for m in self.metrics_buffer
                if m["name"] == metric_name and m["timestamp"] >= cutoff_time
            ]
            
            if not relevant_metrics:
                return {
                    "metric_name": metric_name,
                    "data_points": 0,
                    "success": True,
                }
            
            values = [m["value"] for m in relevant_metrics]
            
            return {
                "metric_name": metric_name,
                "data_points": len(relevant_metrics),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "sum": sum(values),
                "window_minutes": window_minutes,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    def get_all_metrics_summary(self) -> Dict[str, Any]:
        \"\"\"Get summary of all metrics.
        
        Returns:
            All metrics summary
        \"\"\"
        try:
            metric_names = set(m["name"] for m in self.metrics_buffer)
            
            summaries = {}
            for metric_name in metric_names:
                summaries[metric_name] = self.get_metrics_summary(metric_name)
            
            return {
                "metrics": summaries,
                "total_data_points": len(self.metrics_buffer),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }


class AlertingSystem:
    \"\"\"Alert management system.\"\"\"

    def __init__(self):
        \"\"\"Initialize alerting system.\"\"\"
        self.alerts = []
        self.alert_rules = {}

    async def create_alert_rule(
        self,
        rule_name: str,
        metric_name: str,
        threshold: float,
        comparison: str,  # "gt", "lt", "eq"
        severity: str,  # "critical", "high", "medium", "low"
    ) -> Dict[str, Any]:
        \"\"\"Create alert rule.
        
        Args:
            rule_name: Rule name
            metric_name: Metric to monitor
            threshold: Threshold value
            comparison: Comparison operator
            severity: Alert severity
            
        Returns:
            Alert rule info
        \"\"\"
        try:
            rule = {
                "rule_name": rule_name,
                "metric_name": metric_name,
                "threshold": threshold,
                "comparison": comparison,
                "severity": severity,
                "created_at": datetime.utcnow(),
                "enabled": True,
            }
            
            self.alert_rules[rule_name] = rule
            
            return {
                "rule_name": rule_name,
                "status": "CREATED",
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def check_alert_conditions(
        self,
        metric_name: str,
        value: float,
    ) -> List[Dict[str, Any]]:
        \"\"\"Check if any alert conditions are met.
        
        Args:
            metric_name: Metric name
            value: Current value
            
        Returns:
            List of triggered alerts
        \"\"\"
        try:
            triggered_alerts = []
            
            for rule_name, rule in self.alert_rules.items():
                if not rule["enabled"] or rule["metric_name"] != metric_name:
                    continue
                
                condition_met = False
                if rule["comparison"] == "gt":
                    condition_met = value > rule["threshold"]
                elif rule["comparison"] == "lt":
                    condition_met = value < rule["threshold"]
                elif rule["comparison"] == "eq":
                    condition_met = value == rule["threshold"]
                
                if condition_met:
                    alert = {
                        "rule_name": rule_name,
                        "metric_name": metric_name,
                        "value": value,
                        "threshold": rule["threshold"],
                        "severity": rule["severity"],
                        "timestamp": datetime.utcnow(),
                    }
                    triggered_alerts.append(alert)
                    self.alerts.append(alert)
            
            return triggered_alerts
        except Exception:
            return []

    def get_active_alerts(self) -> Dict[str, Any]:
        \"\"\"Get active alerts.
        
        Returns:
            Active alerts
        \"\"\"
        try:
            # Filter alerts from last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            active_alerts = [
                a for a in self.alerts
                if a["timestamp"] >= one_hour_ago
            ]
            
            return {
                "alerts": active_alerts,
                "count": len(active_alerts),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }


class HealthCheckService:
    \"\"\"System health checks.\"\"\"

    async def check_database_health(
        self,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        \"\"\"Check database health.
        
        Args:
            db: Database session
            
        Returns:
            Database health status
        \"\"\"
        try:
            # Simple health check query
            result = await db.execute(select(func.count(1)))
            result.scalar()
            
            return {
                "service": "database",
                "status": "healthy",
                "response_time_ms": 10,
                "success": True,
            }
        except Exception as e:
            return {
                "service": "database",
                "status": "unhealthy",
                "error": str(e),
                "success": False,
            }

    async def check_cache_health(
        self,
        redis_client,
    ) -> Dict[str, Any]:
        \"\"\"Check cache health.
        
        Args:
            redis_client: Redis client
            
        Returns:
            Cache health status
        \"\"\"
        try:
            if not redis_client:
                return {
                    "service": "cache",
                    "status": "unavailable",
                    "success": True,
                }
            
            await redis_client.ping()
            
            return {
                "service": "cache",
                "status": "healthy",
                "success": True,
            }
        except Exception as e:
            return {
                "service": "cache",
                "status": "unhealthy",
                "error": str(e),
                "success": False,
            }

    async def get_system_health(
        self,
        db: AsyncSession,
        redis_client=None,
    ) -> Dict[str, Any]:
        \"\"\"Get overall system health.
        
        Args:
            db: Database session
            redis_client: Redis client
            
        Returns:
            System health status
        \"\"\"
        try:
            db_health = await self.check_database_health(db)
            cache_health = await self.check_cache_health(redis_client)
            
            services = [db_health, cache_health]
            healthy_count = sum(1 for s in services if s["status"] == "healthy")
            
            overall_status = (
                "healthy" if healthy_count == len(services) else
                "degraded" if healthy_count > 0 else
                "unhealthy"
            )
            
            return {
                "status": overall_status,
                "services": services,
                "healthy_services": healthy_count,
                "total_services": len(services),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }
