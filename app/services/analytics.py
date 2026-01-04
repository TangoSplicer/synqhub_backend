"""Analytics and reporting service."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job, Circuit


class AnalyticsService:
    """Generate analytics and reports."""

    @staticmethod
    async def get_user_stats(
        db: AsyncSession,
        user_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get user statistics.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            User statistics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Total jobs
            jobs_result = await db.execute(
                select(func.count(Job.id)).where(
                    Job.user_id == user_id,
                    Job.created_at >= start_date,
                )
            )
            total_jobs = jobs_result.scalar() or 0
            
            # Completed jobs
            completed_result = await db.execute(
                select(func.count(Job.id)).where(
                    Job.user_id == user_id,
                    Job.status == "COMPLETED",
                    Job.created_at >= start_date,
                )
            )
            completed_jobs = completed_result.scalar() or 0
            
            # Failed jobs
            failed_result = await db.execute(
                select(func.count(Job.id)).where(
                    Job.user_id == user_id,
                    Job.status == "FAILED",
                    Job.created_at >= start_date,
                )
            )
            failed_jobs = failed_result.scalar() or 0
            
            # Average execution time
            avg_time_result = await db.execute(
                select(func.avg(Job.execution_time_seconds)).where(
                    Job.user_id == user_id,
                    Job.status == "COMPLETED",
                    Job.created_at >= start_date,
                )
            )
            avg_execution_time = avg_time_result.scalar() or 0
            
            # Total circuits
            circuits_result = await db.execute(
                select(func.count(Circuit.id)).where(
                    Circuit.user_id == user_id,
                    Circuit.created_at >= start_date,
                )
            )
            total_circuits = circuits_result.scalar() or 0
            
            return {
                "period_days": days,
                "total_jobs": total_jobs,
                "completed_jobs": completed_jobs,
                "failed_jobs": failed_jobs,
                "success_rate": (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0,
                "average_execution_time_seconds": float(avg_execution_time),
                "total_circuits": total_circuits,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def get_job_analytics(
        db: AsyncSession,
        user_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get job analytics.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Job analytics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Jobs by type
            result = await db.execute(
                select(Job.job_type, func.count(Job.id)).where(
                    Job.user_id == user_id,
                    Job.created_at >= start_date,
                ).group_by(Job.job_type)
            )
            jobs_by_type = {row[0]: row[1] for row in result.all()}
            
            # Jobs by status
            result = await db.execute(
                select(Job.status, func.count(Job.id)).where(
                    Job.user_id == user_id,
                    Job.created_at >= start_date,
                ).group_by(Job.status)
            )
            jobs_by_status = {row[0]: row[1] for row in result.all()}
            
            # Daily job count
            result = await db.execute(
                select(
                    func.date(Job.created_at).label("date"),
                    func.count(Job.id).label("count"),
                ).where(
                    Job.user_id == user_id,
                    Job.created_at >= start_date,
                ).group_by(func.date(Job.created_at))
                .order_by(func.date(Job.created_at))
            )
            daily_counts = [
                {"date": str(row[0]), "count": row[1]}
                for row in result.all()
            ]
            
            return {
                "jobs_by_type": jobs_by_type,
                "jobs_by_status": jobs_by_status,
                "daily_counts": daily_counts,
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def get_usage_metrics(
        db: AsyncSession,
        user_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get usage metrics.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Usage metrics
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # API calls (estimated from jobs)
            api_calls_result = await db.execute(
                select(func.count(Job.id)).where(
                    Job.user_id == user_id,
                    Job.created_at >= start_date,
                )
            )
            api_calls = api_calls_result.scalar() or 0
            
            # Total compute time
            compute_time_result = await db.execute(
                select(func.sum(Job.execution_time_seconds)).where(
                    Job.user_id == user_id,
                    Job.created_at >= start_date,
                )
            )
            total_compute_time = compute_time_result.scalar() or 0
            
            # Storage usage (estimated)
            storage_result = await db.execute(
                select(func.count(Circuit.id)).where(
                    Circuit.user_id == user_id,
                    Circuit.created_at >= start_date,
                )
            )
            storage_items = storage_result.scalar() or 0
            
            return {
                "period_days": days,
                "api_calls": api_calls,
                "api_calls_per_day": api_calls / days if days > 0 else 0,
                "total_compute_time_seconds": float(total_compute_time),
                "storage_items": storage_items,
                "estimated_storage_mb": storage_items * 0.5,  # Rough estimate
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def get_performance_report(
        db: AsyncSession,
        user_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get performance report.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Performance report
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get completed jobs
            result = await db.execute(
                select(Job.execution_time_seconds).where(
                    Job.user_id == user_id,
                    Job.status == "COMPLETED",
                    Job.created_at >= start_date,
                ).order_by(Job.execution_time_seconds)
            )
            execution_times = [row[0] for row in result.all()]
            
            if not execution_times:
                return {
                    "error": "No completed jobs in period",
                    "success": False,
                }
            
            # Calculate percentiles
            sorted_times = sorted(execution_times)
            n = len(sorted_times)
            
            return {
                "period_days": days,
                "total_jobs": n,
                "min_time_seconds": float(min(execution_times)),
                "max_time_seconds": float(max(execution_times)),
                "avg_time_seconds": float(sum(execution_times) / n),
                "median_time_seconds": float(sorted_times[n // 2]),
                "p95_time_seconds": float(sorted_times[int(n * 0.95)]),
                "p99_time_seconds": float(sorted_times[int(n * 0.99)]),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }


class ReportingService:
    """Generate reports."""

    @staticmethod
    async def generate_usage_report(
        db: AsyncSession,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Generate usage report.
        
        Args:
            db: Database session
            user_id: User ID
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Usage report
        """
        try:
            days = (end_date - start_date).days
            
            stats = await AnalyticsService.get_user_stats(db, user_id, days)
            job_analytics = await AnalyticsService.get_job_analytics(db, user_id, days)
            usage = await AnalyticsService.get_usage_metrics(db, user_id, days)
            
            return {
                "report_type": "usage",
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "days": days,
                },
                "statistics": stats,
                "job_analytics": job_analytics,
                "usage_metrics": usage,
                "generated_at": datetime.utcnow().isoformat(),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }

    @staticmethod
    async def generate_performance_report(
        db: AsyncSession,
        user_id: str,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Generate performance report.
        
        Args:
            db: Database session
            user_id: User ID
            days: Number of days to analyze
            
        Returns:
            Performance report
        """
        try:
            perf = await AnalyticsService.get_performance_report(db, user_id, days)
            
            return {
                "report_type": "performance",
                "period_days": days,
                "performance": perf,
                "generated_at": datetime.utcnow().isoformat(),
                "success": True,
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False,
            }
