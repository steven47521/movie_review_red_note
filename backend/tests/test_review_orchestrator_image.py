from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.session import Base
from app.models.creation_session import CreationSession, SessionStatus
from app.models.draft_version import DraftVersion
from app.models.image_asset import ImageAsset
from app.models.movie_meta import MovieMeta
from app.models.review_message import ReviewMessage
from app.llm.prompts.image_reviewer import IMAGE_MODERATOR_SYSTEM, IMAGE_REVIEWER_SYSTEM
from app.services.review_orchestrator import ReviewOrchestrator, ReviewRoundLimitError
from app.services.visual_service import VisualService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def image_ready_session(db_session):
    creation = CreationSession(
        movie_title="肖申克的救赎",
        status=SessionStatus.IMAGE_REVIEWING.value,
        selected_angle={"id": "a1", "title": "体制与希望"},
        reviewer_panel_ids=["p1", "p2", "p3"],
        image_review_round=0,
    )
    db_session.add(creation)
    db_session.commit()
    db_session.add(
        MovieMeta(
            session_id=creation.id,
            title="The Shawshank Redemption",
            year=1994,
            genres=["Drama"],
        )
    )
    db_session.add(
        DraftVersion(
            session_id=creation.id,
            version=1,
            title="标题",
            hooks=["hook1"],
            body="正文讨论自由。",
            tags=["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
            review_round=1,
        )
    )
    for i, t in enumerate(["cover", "quote_card", "mood_shot"]):
        db_session.add(
            ImageAsset(
                session_id=creation.id,
                type=t,
                url=f"https://cdn.example/{t}.png",
                prompt=f"prompt {t}",
                style_key="drama_film",
                version=1,
                review_round=0,
            )
        )
    db_session.commit()
    return creation


def test_image_review_attaches_image_id_to_message(db_session, image_ready_session):
    llm = MagicMock()
    reviewer_responses = [
        {"content": "封面氛围好，金句卡字体可更大。", "scores": {"style": 8}},
        {"content": "整体小红书感不错。", "scores": {"aesthetic": 7}},
        {"content": "氛围图与主题一致。", "scores": {"consistency": 8}},
    ]
    reviewer_calls = 0

    def complete_json(system, user):
        nonlocal reviewer_calls
        if system == IMAGE_REVIEWER_SYSTEM:
            response = reviewer_responses[reviewer_calls % len(reviewer_responses)]
            reviewer_calls += 1
            return response
        if system == IMAGE_MODERATOR_SYSTEM:
            return {
                "content": "建议优化 quote_card 排版。",
                "regenerate_types": ["quote_card"],
            }
        raise AssertionError(f"unexpected system prompt: {system[:40]}")

    llm.complete_json.side_effect = complete_json
    image_client = MagicMock()
    image_client.generate.return_value = "https://cdn.example/quote_card_v2.png"

    orch = ReviewOrchestrator(
        llm_client=llm,
        persona_loader=lambda ids: [
            {"id": i, "nickname": f"审稿{i}", "mbti": "ISFP", "age_band": "30s", "avatar_url": "/a.png"}
            for i in ids
        ],
        visual_service=VisualService(db=db_session, image_client=image_client),
    )
    orch.run_image_review_round(db_session, image_ready_session.id)

    msg = (
        db_session.query(ReviewMessage)
        .filter_by(session_id=image_ready_session.id, phase="image")
        .first()
    )
    assert msg is not None
    assert msg.attachment is not None


def test_image_review_round_limit_five():
    orch = ReviewOrchestrator(max_rounds=5)
    with pytest.raises(ReviewRoundLimitError):
        orch.ensure_can_continue_image(image_review_round=5)
