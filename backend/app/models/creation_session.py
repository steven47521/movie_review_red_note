import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class SessionStatus(str, enum.Enum):
    CREATED = "created"
    RESEARCHING = "researching"
    ANGLES_READY = "angles_ready"
    ROUTE_READY = "route_ready"
    DRAFTING = "drafting"
    TEXT_REVIEWING = "text_reviewing"
    TEXT_FINALIZED = "text_finalized"
    IMAGE_GENERATING = "image_generating"
    IMAGE_REVIEWING = "image_reviewing"
    COMPLETED = "completed"


class CreationSession(Base):
    __tablename__ = "creation_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )
    movie_title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default=SessionStatus.CREATED.value, nullable=False
    )
    angle_candidates: Mapped[list | None] = mapped_column(JSON, nullable=True)
    route_candidates: Mapped[list | None] = mapped_column(JSON, nullable=True)
    selected_angle: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    selected_route: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reviewer_panel_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    text_review_round: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    image_review_round: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    movie_meta: Mapped["MovieMeta | None"] = relationship(
        back_populates="session", uselist=False
    )
    research_snapshots: Mapped[list["ResearchSnapshot"]] = relationship(
        back_populates="session"
    )
    review_messages: Mapped[list["ReviewMessage"]] = relationship(
        back_populates="session"
    )
    draft_versions: Mapped[list["DraftVersion"]] = relationship(
        back_populates="session"
    )
    image_assets: Mapped[list["ImageAsset"]] = relationship(back_populates="session")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="session")
