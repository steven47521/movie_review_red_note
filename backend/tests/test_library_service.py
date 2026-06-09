import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.session import Base
from app.models.creation_session import CreationSession, SessionStatus
from app.models.draft_version import DraftVersion
from app.models.image_asset import ImageAsset
from app.models.movie_meta import MovieMeta
from app.models.research_snapshot import ResearchSnapshot
from app.models.review_message import ReviewMessage
from app.services.library_service import LibraryService, LibraryServiceError


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def completed_session(db_session):
    s1 = CreationSession(
        movie_title="肖申克的救赎",
        status=SessionStatus.COMPLETED.value,
        is_favorite=True,
        is_published=False,
    )
    s2 = CreationSession(
        movie_title="2001太空漫游",
        status=SessionStatus.COMPLETED.value,
        is_favorite=False,
        is_published=True,
    )
    db_session.add_all([s1, s2])
    db_session.commit()

    for session in (s1, s2):
        db_session.add(
            MovieMeta(session_id=session.id, title=session.movie_title, year=1994)
        )
        db_session.add(
            ResearchSnapshot(
                session_id=session.id,
                opinions=[{"text": "opinion", "source": "search"}] * 3,
                sources_summary="search",
            )
        )
        db_session.add(
            ReviewMessage(
                session_id=session.id,
                phase="text",
                round=1,
                role="reviewer",
                content="不错的稿子",
            )
        )
        db_session.add(
            DraftVersion(
                session_id=session.id,
                version=1,
                title="标题",
                hooks=["hook"],
                body="正文",
                tags=["#t1", "#t2", "#t3", "#t4", "#t5"],
                review_round=1,
            )
        )
        db_session.add(
            ImageAsset(
                session_id=session.id,
                type="cover",
                url="https://cdn.example/cover.png",
                prompt="prompt",
                style_key="drama_film",
                version=1,
                review_round=1,
            )
        )
    db_session.commit()
    return s1


def test_timeline_includes_research_messages_and_drafts(db_session, completed_session):
    svc = LibraryService(db=db_session)
    timeline = svc.get_timeline(completed_session.id)
    event_types = {e["type"] for e in timeline}
    assert "research" in event_types
    assert "review_message" in event_types
    assert "draft_version" in event_types
    assert "image_asset" in event_types


def test_filter_published_sessions(db_session, completed_session):
    svc = LibraryService(db=db_session)
    published = svc.list_sessions(is_published=True)
    assert len(published) == 1
    assert all(s.is_published for s in published)


def test_filter_favorite_sessions(db_session, completed_session):
    svc = LibraryService(db=db_session)
    favorites = svc.list_sessions(is_favorite=True)
    assert len(favorites) == 1
    assert favorites[0].movie_title == "肖申克的救赎"


def test_update_flags(db_session, completed_session):
    svc = LibraryService(db=db_session)
    updated = svc.update_flags(
        completed_session.id, is_favorite=False, is_published=True
    )
    assert updated.is_favorite is False
    assert updated.is_published is True


def test_get_session_detail(db_session, completed_session):
    svc = LibraryService(db=db_session)
    detail = svc.get_session_detail(completed_session.id)
    assert detail["movie_title"] == "肖申克的救赎"
    assert detail["status"] == SessionStatus.COMPLETED.value
    assert "movie" in detail


def test_delete_session_removes_related_records(db_session):
    session = CreationSession(movie_title="待删除", status=SessionStatus.CREATED.value)
    db_session.add(session)
    db_session.commit()

    db_session.add(
        MovieMeta(session_id=session.id, title="待删除", year=2000, genres=["Drama"])
    )
    db_session.add(
        ResearchSnapshot(
            session_id=session.id,
            opinions=[{"text": "观点", "source": "search"}],
            sources_summary="search",
        )
    )
    db_session.commit()

    svc = LibraryService(db=db_session)
    svc.delete_session(session.id)

    assert db_session.get(CreationSession, session.id) is None
    assert db_session.query(MovieMeta).filter_by(session_id=session.id).count() == 0
    assert (
        db_session.query(ResearchSnapshot).filter_by(session_id=session.id).count() == 0
    )


def test_timeline_not_found(db_session):
    svc = LibraryService(db=db_session)
    with pytest.raises(LibraryServiceError):
        svc.get_timeline("missing-id")
