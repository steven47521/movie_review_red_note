import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ReviewPhase(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"


class MessageRole(str, enum.Enum):
    REVIEWER = "reviewer"
    MODERATOR = "moderator"
    WRITER = "writer"
    USER = "user"
    SYSTEM = "system"


class ReviewMessage(Base):
    __tablename__ = "review_messages"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("creation_sessions.id"), nullable=False
    )
    phase: Mapped[str] = mapped_column(String(16), nullable=False)
    round: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    persona_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("reviewer_personas.id"), nullable=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    attachment: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    session: Mapped["CreationSession"] = relationship(back_populates="review_messages")
    persona: Mapped["ReviewerPersona | None"] = relationship()
