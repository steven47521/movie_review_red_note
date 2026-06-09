import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.db.session import Base
from app.models import (  # noqa: F401 — register models on Base.metadata
    audit_log,
    creation_session,
    draft_version,
    image_asset,
    movie_meta,
    research_snapshot,
    review_message,
    reviewer_persona,
    user,
)
from app.models.creation_session import CreationSession, SessionStatus


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(eng)
    return eng


def test_core_tables_exist(engine):
    tables = set(inspect(engine).get_table_names())
    expected = {
        "users",
        "reviewer_personas",
        "creation_sessions",
        "movie_meta",
        "research_snapshots",
        "review_messages",
        "draft_versions",
        "image_assets",
        "audit_logs",
    }
    assert expected.issubset(tables)


def test_creation_session_defaults(engine):
    with Session(engine) as db:
        session = CreationSession(movie_title="肖申克的救赎")
        db.add(session)
        db.commit()
        db.refresh(session)

    assert session.status == SessionStatus.CREATED.value
    assert session.text_review_round == 0
    assert session.image_review_round == 0
    assert session.is_favorite is False
    assert session.is_published is False
