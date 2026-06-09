from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@patch("app.api.routes.sessions.ResearchService")
def test_create_session_and_research(mock_service_cls):
    mock_svc = MagicMock()
    mock_svc.research_and_persist.return_value = {
        "session_id": "sess-1",
        "movie": {
            "title": "The Shawshank Redemption",
            "year": 1994,
            "director": "Frank Darabont",
            "genres": ["Drama"],
            "country": "USA",
            "tmdb_id": 278,
        },
        "opinions": [
            {"text": "hope", "source": "search"},
            {"text": "freedom", "source": "search"},
            {"text": "friendship", "source": "tmdb"},
        ],
        "sources_summary": "search, tmdb",
        "snapshot_id": "snap-1",
    }
    mock_service_cls.return_value = mock_svc

    create_resp = client.post(
        "/api/v1/sessions", json={"title": "肖申克的救赎", "year": 1994}
    )
    assert create_resp.status_code == 200
    session_id = create_resp.json()["id"]

    research_resp = client.post(f"/api/v1/sessions/{session_id}/research")
    assert research_resp.status_code == 200
    data = research_resp.json()
    assert data["movie"]["year"] == 1994
    assert len(data["opinions"]) >= 3
