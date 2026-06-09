import uuid

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ReviewerPersona(Base):
    __tablename__ = "reviewer_personas"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    mbti: Mapped[str] = mapped_column(String(4), nullable=False)
    age_band: Mapped[str] = mapped_column(String(10), nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(512), nullable=False)
    taste_profile: Mapped[dict] = mapped_column(JSON, nullable=False)
