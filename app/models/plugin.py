"""Plugin Registry model for SynQHub."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Plugin(Base):
    """Plugin Registry model."""

    __tablename__ = "plugins"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    author_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    documentation_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    plugin_code: Mapped[str] = mapped_column(String(50000), nullable=False)
    dependencies: Mapped[list | None] = mapped_column(JSON, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    downloads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rating: Mapped[float | None] = mapped_column(nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_updated_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    def __repr__(self) -> str:
        return f"<Plugin {self.name} v{self.version}>"


class PluginReview(Base):
    """Plugin review and rating model."""

    __tablename__ = "plugin_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    plugin_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    reviewer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    review_text: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<PluginReview plugin_id={self.plugin_id} rating={self.rating}>"
