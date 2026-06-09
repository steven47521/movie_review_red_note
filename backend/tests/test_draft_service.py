from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.session import Base
from app.models.creation_session import CreationSession
from app.models.draft_version import DraftVersion
from app.models.review_message import ReviewMessage
from app.services.draft_service import DraftService, DraftServiceError


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def sample_draft(db_session):
    creation = CreationSession(movie_title="肖申克的救赎")
    db_session.add(creation)
    db_session.commit()

    draft = DraftVersion(
        session_id=creation.id,
        version=1,
        title="这部电影很好看",
        hooks=["值得一看", "经典之作"],
        body="综上所述，这部电影深刻地揭示了人性的复杂。",
        tags=["#经典电影", "#深度影评", "#肖申克", "#电影", "#影评"],
        review_round=1,
    )
    db_session.add(draft)
    db_session.commit()
    return draft


def test_regenerate_title_only_keeps_body(db_session, sample_draft):
    llm = MagicMock()
    llm.complete_json.return_value = {"title": "当习惯成为牢笼"}
    svc = DraftService(db=db_session, llm_client=llm)

    new_version = svc.regenerate_part(sample_draft.session_id, part="title")

    assert new_version.title != sample_draft.title
    assert new_version.body == sample_draft.body
    assert new_version.hooks == sample_draft.hooks
    assert new_version.tags == sample_draft.tags
    assert new_version.version == sample_draft.version + 1


def test_de_ai_polish_reduces_banned_phrases():
    body = "综上所述，这部电影深刻地揭示了人性的复杂。"
    polished = DraftService.de_ai_polish(body)
    assert "综上所述" not in polished


def test_de_ai_polish_persists_new_version(db_session, sample_draft):
    llm = MagicMock()
    llm.complete_json.return_value = {
        "body": "从制度化视角看，主角的反抗是认知层面的越狱。"
    }
    svc = DraftService(db=db_session, llm_client=llm)

    new_version = svc.apply_de_ai_polish(sample_draft.session_id)

    assert "综上所述" not in new_version.body
    assert new_version.version == sample_draft.version + 1


def test_manual_patch_creates_version_and_writer_message(db_session, sample_draft):
    svc = DraftService(db=db_session)

    new_version = svc.manual_patch(
        sample_draft.session_id,
        {"title": "我手动改的标题", "body": sample_draft.body},
    )

    assert new_version.title == "我手动改的标题"
    assert new_version.version == 2

    writer_msg = (
        db_session.query(ReviewMessage)
        .filter_by(session_id=sample_draft.session_id, role="writer")
        .first()
    )
    assert writer_msg is not None
    assert "手动" in writer_msg.content


def test_regenerate_invalid_part_raises():
    svc = DraftService()
    with pytest.raises(DraftServiceError):
        svc.regenerate_part("fake-id", part="invalid")
