"""Job model for quantum job tracking."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Job(Base):
    """Quantum job model."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    backend: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=\"SUBMITTED\", nullable=False, index=True)
    circuit_data: Mapped[dict] = mapped_column(JSON, nullable=True)
    parameters: Mapped[dict] = mapped_column(JSON, nullable=True)
    results: Mapped[dict] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    execution_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resource_usage: Mapped[dict] = mapped_column(JSON, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f\"<Job {self.id} ({self.job_type})>\"
