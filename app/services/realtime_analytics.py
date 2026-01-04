"""Real-time analytics engine with streaming data."""

import asyncio
from datetime import datetime, timedelta
from typing import Any, AsyncGenerator, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job, Circuit


class RealtimeAnalyticsEngine:
    """Real-time analytics with streaming data."""

    def __init__(self, redis_client=None):
        """Initialize real-time analytics engine.
        
        Args:
            redis_client: Redis client for caching
        """
        self.redis = redis_client
        self.metrics_buffer = {}
        self.event_stream = asyncio.Queue()

    async def stream_job_metrics(
        self,
        db: AsyncSession,
        user_id: str,
        interval_seconds: int = 5,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream job metrics in real-time.
        
        Args:
            db: Database session
            user_id: User ID
            interval_seconds: Update interval
            
        Yields:
            Metric updates
        """
        try:
            while True:
                # Get current metrics
                result = await db.execute(
                    select(
                        func.count(Job.id).label("total"),
                        func.sum(
                            func.case(
                                (Job.status == "COMPLETED", 1),
                                else_=0
                            )
                        ).label("completed"),
                        func.sum(
                            func.case(
                                (Job.status == "FAILED", 1),
                                else_=0
                            )
                        ).label("failed"),
                        func.avg(Job.execution_time_seconds).label("avg_time"),
                    ).where(Job.user_id == user_id)
                )
                row = result.first()
                
                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_jobs": row[0] or 0,
                    "completed_jobs": row[1] or 0,
                    "failed_jobs": row[2] or 0,
                    "average_execution_time": float(row[3] or 0),
                    "success_rate": (
                        (row[1] or 0) / (row[0] or 1) * 100
                    ),
                }
                
                yield metrics
                await asyncio.sleep(interval_seconds)
        except Exception as e:
            yield {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def stream_circuit_metrics(
        self,
        db: AsyncSession,
        user_id: str,
        interval_seconds: int = 5,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream circuit metrics in real-time.
        
        Args:
            db: Database session
            user_id: User ID
            interval_seconds: Update interval
            
        Yields:
            Circuit metric updates
        """
        try:
            while True:
                # Get circuit metrics
                result = await db.execute(
                    select(
                        func.count(Circuit.id).label("total"),
                        func.avg(Circuit.gate_count).label("avg_gates"),
                        func.avg(Circuit.qubit_count).label("avg_qubits"),
                        func.max(Circuit.gate_count).label("max_gates"),
                    ).where(Circuit.user_id == user_id)
                )
                row = result.first()
                
                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "total_circuits": row[0] or 0,
                    "average_gates": float(row[1] or 0),
                    "average_qubits": float(row[2] or 0),
                    "max_gates": row[3] or 0,
                }
                
                yield metrics
                await asyncio.sleep(interval_seconds)
        except Exception as e:
            yield {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    async def get_live_dashboard(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        """Get live dashboard data.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Live dashboard data
        """
        try:
            # Get jobs in last hour
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            
            result = await db.execute(
                select(
                    func.count(Job.id).label("jobs_last_hour"),
                    func.sum(
                        func.case(
                            (Job.status == "COMPLETED", 1),
                            else_=0
                        )
                    ).label("completed_last_hour"),
                    func.sum(
                        func.case(
                            (Job.status == "QUEUED", 1),
                            else_=0
                        )
                    ).label("queued_jobs"),
                    func.sum(
                        func.case(
                            (Job.status == "RUNNING", 1),
                            else_=0
                        )
                    ).label("running_jobs"),
                ).where(
                    Job.user_id == user_id,
                    Job.created_at >= one_hour_ago,
                )
            )
            row = result.first()
            
            # Get average metrics
            avg_result = await db.execute(
                select(
                    func.avg(Job.execution_time_seconds).label("avg_time"),
                    func.max(Job.execution_time_seconds).label("max_time"),
                ).where(
                    Job.user_id == user_id,
                    Job.status == "COMPLETED",
                    Job.created_at >= one_hour_ago,
                )
            )
            avg_row = avg_result.first()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "jobs_last_hour": row[0] or 0,
                "completed_last_hour": row[1] or 0,
                "queued_jobs": row[2] or 0,
                "running_jobs": row[3] or 0,
                "average_execution_time": float(avg_row[0] or 0),
                "max_execution_time": float(avg_row[1] or 0),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def track_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Track custom metric.
        
        Args:
            metric_name: Metric name
            value: Metric value
            tags: Optional tags
        """
        try:
            metric_data = {
                "name": metric_name,
                "value": value,
                "tags": tags or {},
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # Store in Redis if available
            if self.redis:
                await self.redis.lpush(
                    f"metrics:{metric_name}",
                    str(metric_data),
                )
                # Keep last 1000 metrics
                await self.redis.ltrim(
                    f"metrics:{metric_name}",
                    0,
                    999,
                )
            
            # Add to event stream
            await self.event_stream.put(metric_data)
        except Exception:
            pass

    async def get_metric_timeseries(
        self,
        metric_name: str,
        hours: int = 1,
    ) -> Dict[str, Any]:
        """Get metric time series.
        
        Args:
            metric_name: Metric name
            hours: Hours to retrieve
            
        Returns:
            Time series data
        """
        try:
            if not self.redis:
                return {
                    "error": "Redis not configured",
                    "success": False,
                }
            
            # Get metrics from Redis
            metrics = await self.redis.lrange(
                f"metrics:{metric_name}",
                0,
                -1,
            )
            
            return {
                "metric_name": metric_name,
                "data_points": len(metrics),
                "hours": hours,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }


class StreamingDataProcessor:
    """Process streaming data in real-time."""

    def __init__(self):
        """Initialize streaming processor."""
        self.processors = {}

    async def process_job_stream(
        self,
        job_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Process job stream data.
        
        Args:
            job_data: Job data
            
        Returns:
            Processed data
        """
        try:
            processed = {
                "job_id": job_data.get("id"),
                "status": job_data.get("status"),
                "execution_time": job_data.get("execution_time_seconds"),
                "success": job_data.get("status") == "COMPLETED",
                "timestamp": datetime.utcnow().isoformat(),
            }
            
            # Calculate metrics
            if processed["execution_time"]:
                processed["performance_score"] = min(
                    100,
                    (100 * 10) / processed["execution_time"],
                )
            
            return processed
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def aggregate_metrics(
        self,
        metrics: List[Dict[str, Any]],
        window_seconds: int = 60,
    ) -> Dict[str, Any]:
        """Aggregate metrics over time window.
        
        Args:
            metrics: List of metrics
            window_seconds: Aggregation window
            
        Returns:
            Aggregated metrics
        """
        try:
            if not metrics:
                return {
                    "error": "No metrics provided",
                    "success": False,
                }
            
            values = [m.get("value", 0) for m in metrics]
            
            return {
                "count": len(metrics),
                "sum": sum(values),
                "average": sum(values) / len(values) if values else 0,
                "min": min(values) if values else 0,
                "max": max(values) if values else 0,
                "window_seconds": window_seconds,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }
