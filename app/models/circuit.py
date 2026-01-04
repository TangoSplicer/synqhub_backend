"""Circuit model for storing quantum circuits."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Circuit(Base):
    """Quantum circuit model."""

    __tablename__ = "circuits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    circuit_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    depth: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gate_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    qubit_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tags: Mapped[list | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f\"<Circuit {self.name or self.id}>\"
