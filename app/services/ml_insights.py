"""ML-based insights and anomaly detection."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job


class AnomalyDetectionEngine:
    """Detect anomalies in quantum job execution."""

    def __init__(self):
        """Initialize anomaly detection engine."""
        self.baseline_metrics = {}
        self.anomaly_threshold = 2.0  # Standard deviations

    async def analyze_execution_time(
        self,
        db: AsyncSession,
        user_id: str,
        job_id: str,
        execution_time: float,
    ) -> Dict[str, Any]:
        """Analyze job execution time for anomalies.
        
        Args:
            db: Database session
            user_id: User ID
            job_id: Job ID
            execution_time: Execution time in seconds
            
        Returns:
            Anomaly analysis
        """
        try:
            # Get historical execution times
            result = await db.execute(
                select(
                    func.avg(Job.execution_time_seconds).label("avg"),
                    func.stddev(Job.execution_time_seconds).label("stddev"),
                ).where(
                    Job.user_id == user_id,
                    Job.status == "COMPLETED",
                    Job.created_at >= datetime.utcnow() - timedelta(days=30),
                )
            )
            row = result.first()
            
            avg_time = float(row[0] or 0)
            stddev = float(row[1] or 1)
            
            # Calculate z-score
            if stddev > 0:
                z_score = (execution_time - avg_time) / stddev
            else:
                z_score = 0
            
            is_anomaly = abs(z_score) > self.anomaly_threshold
            
            return {
                "job_id": job_id,
                "execution_time": execution_time,
                "average_time": avg_time,
                "standard_deviation": stddev,
                "z_score": z_score,
                "is_anomaly": is_anomaly,
                "anomaly_type": (
                    "slow" if z_score > self.anomaly_threshold else
                    "fast" if z_score < -self.anomaly_threshold else
                    "normal"
                ),
                "confidence": min(100, abs(z_score) * 50),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def detect_failure_patterns(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        """Detect failure patterns.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Failure pattern analysis
        """
        try:
            # Get recent failures
            result = await db.execute(
                select(Job.job_type, func.count(Job.id).label("count")).where(
                    Job.user_id == user_id,
                    Job.status == "FAILED",
                    Job.created_at >= datetime.utcnow() - timedelta(days=7),
                ).group_by(Job.job_type)
            )
            failures_by_type = {row[0]: row[1] for row in result.all()}
            
            # Get total jobs by type
            result = await db.execute(
                select(Job.job_type, func.count(Job.id).label("count")).where(
                    Job.user_id == user_id,
                    Job.created_at >= datetime.utcnow() - timedelta(days=7),
                ).group_by(Job.job_type)
            )
            total_by_type = {row[0]: row[1] for row in result.all()}
            
            # Calculate failure rates
            patterns = {}
            for job_type, total in total_by_type.items():
                failures = failures_by_type.get(job_type, 0)
                failure_rate = (failures / total * 100) if total > 0 else 0
                
                if failure_rate > 10:  # Alert if > 10% failure rate
                    patterns[job_type] = {
                        "failure_rate": failure_rate,
                        "failures": failures,
                        "total": total,
                        "severity": (
                            "critical" if failure_rate > 50 else
                            "high" if failure_rate > 25 else
                            "medium"
                        ),
                    }
            
            return {
                "patterns": patterns,
                "period_days": 7,
                "has_anomalies": len(patterns) > 0,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def predict_job_duration(
        self,
        db: AsyncSession,
        user_id: str,
        job_type: str,
    ) -> Dict[str, Any]:
        """Predict job duration based on historical data.
        
        Args:
            db: Database session
            user_id: User ID
            job_type: Job type
            
        Returns:
            Duration prediction
        """
        try:
            # Get historical data for job type
            result = await db.execute(
                select(
                    func.avg(Job.execution_time_seconds).label("avg"),
                    func.min(Job.execution_time_seconds).label("min"),
                    func.max(Job.execution_time_seconds).label("max"),
                    func.stddev(Job.execution_time_seconds).label("stddev"),
                ).where(
                    Job.user_id == user_id,
                    Job.job_type == job_type,
                    Job.status == "COMPLETED",
                    Job.created_at >= datetime.utcnow() - timedelta(days=30),
                )
            )
            row = result.first()
            
            avg_time = float(row[0] or 0)
            min_time = float(row[1] or 0)
            max_time = float(row[2] or 0)
            stddev = float(row[3] or 0)
            
            # Calculate confidence interval
            confidence_interval = 1.96 * stddev if stddev > 0 else 0
            
            return {
                "job_type": job_type,
                "predicted_duration_seconds": avg_time,
                "min_duration": min_time,
                "max_duration": max_time,
                "confidence_interval": confidence_interval,
                "lower_bound": max(0, avg_time - confidence_interval),
                "upper_bound": avg_time + confidence_interval,
                "confidence_level": 95,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def get_optimization_recommendations(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        """Get optimization recommendations.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Optimization recommendations
        """
        try:
            recommendations = []
            
            # Analyze failure patterns
            failures = await self.detect_failure_patterns(db, user_id)
            if failures["has_anomalies"]:
                for job_type, pattern in failures["patterns"].items():
                    recommendations.append({
                        "type": "high_failure_rate",
                        "job_type": job_type,
                        "failure_rate": pattern["failure_rate"],
                        "recommendation": f"Investigate {job_type} jobs with {pattern['failure_rate']:.1f}% failure rate",
                        "priority": "high" if pattern["severity"] == "critical" else "medium",
                    })
            
            # Analyze execution times
            result = await db.execute(
                select(
                    func.avg(Job.execution_time_seconds).label("avg"),
                ).where(
                    Job.user_id == user_id,
                    Job.status == "COMPLETED",
                    Job.created_at >= datetime.utcnow() - timedelta(days=7),
                )
            )
            row = result.first()
            avg_time = float(row[0] or 0)
            
            if avg_time > 120:  # > 2 minutes
                recommendations.append({
                    "type": "slow_execution",
                    "average_time": avg_time,
                    "recommendation": "Consider optimizing circuits or using different backends",
                    "priority": "medium",
                })
            
            return {
                "recommendations": recommendations,
                "count": len(recommendations),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }


class InsightGenerator:
    """Generate insights from quantum computing data."""

    async def generate_performance_insights(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        """Generate performance insights.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Performance insights
        """
        try:
            insights = []
            
            # Get performance metrics
            result = await db.execute(
                select(
                    func.count(Job.id).label("total"),
                    func.sum(
                        func.case(
                            (Job.status == "COMPLETED", 1),
                            else_=0
                        )
                    ).label("completed"),
                    func.avg(Job.execution_time_seconds).label("avg_time"),
                ).where(
                    Job.user_id == user_id,
                    Job.created_at >= datetime.utcnow() - timedelta(days=7),
                )
            )
            row = result.first()
            
            total = row[0] or 0
            completed = row[1] or 0
            avg_time = float(row[2] or 0)
            
            success_rate = (completed / total * 100) if total > 0 else 0
            
            if success_rate > 95:
                insights.append({
                    "type": "positive",
                    "message": f"Excellent success rate of {success_rate:.1f}%",
                    "metric": "success_rate",
                })
            elif success_rate < 80:
                insights.append({
                    "type": "warning",
                    "message": f"Success rate is {success_rate:.1f}%, consider investigating failures",
                    "metric": "success_rate",
                })
            
            if avg_time < 30:
                insights.append({
                    "type": "positive",
                    "message": f"Fast execution time: {avg_time:.1f}s average",
                    "metric": "execution_time",
                })
            
            return {
                "insights": insights,
                "period_days": 7,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    async def generate_usage_insights(
        self,
        db: AsyncSession,
        user_id: str,
    ) -> Dict[str, Any]:
        """Generate usage insights.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Usage insights
        """
        try:
            insights = []
            
            # Get usage by job type
            result = await db.execute(
                select(Job.job_type, func.count(Job.id).label("count")).where(
                    Job.user_id == user_id,
                    Job.created_at >= datetime.utcnow() - timedelta(days=30),
                ).group_by(Job.job_type)
                .order_by(func.count(Job.id).desc())
            )
            usage_by_type = result.all()
            
            if usage_by_type:
                top_type = usage_by_type[0][0]
                top_count = usage_by_type[0][1]
                insights.append({
                    "type": "info",
                    "message": f"Most used algorithm: {top_type} ({top_count} jobs)",
                    "metric": "top_algorithm",
                })
            
            return {
                "insights": insights,
                "period_days": 30,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }
