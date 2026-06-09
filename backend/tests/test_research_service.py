from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.session import Base
from app.models.creation_session import CreationSession, SessionStatus
from app.models.movie_meta import MovieMeta
from app.models.research_snapshot import ResearchSnapshot
from app.clients.tmdb_client import TMDBClientError
from app.services.research_service import ResearchService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_research_returns_at_least_three_opinions():
    tmdb = MagicMock()
    tmdb.search.return_value = {
        "title": "The Shawshank Redemption",
        "year": 1994,
        "director": "Frank Darabont",
        "genres": ["Drama", "Crime"],
        "country": "USA",
        "tmdb_id": 278,
        "raw_metadata": {},
    }
    search = MagicMock()
    search.fetch_opinions.return_value = [
        {"text": "hope and institutionalization", "source": "search"},
        {"text": "friendship as resistance", "source": "search"},
        {"text": "freedom metaphor", "source": "douban"},
    ]

    svc = ResearchService(tmdb_client=tmdb, search_client=search)
    result = svc.research("肖申克的救赎")

    assert result["movie"]["year"] == 1994
    assert len(result["opinions"]) >= 3
    tmdb.search.assert_called_once()
    search.fetch_opinions.assert_called_once()


def test_research_falls_back_when_tmdb_unreachable():
    tmdb = MagicMock()
    tmdb.search.side_effect = TMDBClientError("TMDB request failed: timeout")
    search = MagicMock()
    search.fetch_opinions.return_value = [
        {"text": "主题深度讨论", "source": "search"},
        {"text": "人物关系解读", "source": "search"},
        {"text": "影像风格分析", "source": "fallback"},
    ]

    svc = ResearchService(tmdb_client=tmdb, search_client=search)
    result = svc.research("肖申克的救赎", year=1994)

    assert result["movie"]["title"] == "肖申克的救赎"
    assert result["movie"]["year"] == 1994
    assert len(result["opinions"]) >= 3


def test_research_persists_movie_meta_and_snapshot(db_session):
    tmdb = MagicMock()
    tmdb.search.return_value = {
        "title": "2001: A Space Odyssey",
        "year": 1968,
        "director": "Stanley Kubrick",
        "genres": ["Sci-Fi"],
        "country": "UK",
        "tmdb_id": 62,
        "raw_metadata": {"overview": "Sci-fi classic"},
    }
    search = MagicMock()
    search.fetch_opinions.return_value = [
        {"text": "existential AI", "source": "search"},
        {"text": "human evolution", "source": "search"},
        {"text": "technology anxiety", "source": "tmdb"},
    ]

    creation = CreationSession(movie_title="2001太空漫游")
    db_session.add(creation)
    db_session.commit()

    svc = ResearchService(tmdb_client=tmdb, search_client=search)
    result = svc.research_and_persist(db_session, creation.id, "2001太空漫游")

    db_session.refresh(creation)
    meta = db_session.query(MovieMeta).filter_by(session_id=creation.id).one()
    snapshot = (
        db_session.query(ResearchSnapshot).filter_by(session_id=creation.id).one()
    )

    assert creation.status == SessionStatus.ANGLES_READY.value
    assert meta.year == 1968
    assert meta.genres == ["Sci-Fi"]
    assert len(snapshot.opinions) >= 3
    assert result["opinions"] == snapshot.opinions
