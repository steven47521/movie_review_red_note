from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.session import Base
from app.models.creation_session import CreationSession, SessionStatus
from app.models.movie_meta import MovieMeta
from app.models.research_snapshot import ResearchSnapshot
from app.services.ideation_service import IdeationService, IdeationServiceError


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def researched_session(db_session):
    creation = CreationSession(
        movie_title="肖申克的救赎", status=SessionStatus.ANGLES_READY.value
    )
    db_session.add(creation)
    db_session.commit()

    db_session.add(
        MovieMeta(
            session_id=creation.id,
            title="The Shawshank Redemption",
            year=1994,
            director="Frank Darabont",
            genres=["Drama", "Crime"],
        )
    )
    db_session.add(
        ResearchSnapshot(
            session_id=creation.id,
            opinions=[
                {"text": "体制与人性", "source": "search"},
                {"text": "希望作为抵抗", "source": "tmdb"},
                {"text": "友谊与自由", "source": "douban"},
            ],
            sources_summary="search, tmdb, douban",
        )
    )
    db_session.commit()
    return creation


def test_generate_angles_returns_theme_not_plot():
    llm = MagicMock()
    llm.complete_json.return_value = {
        "angles": [
            {"id": "a1", "title": "体制与希望", "description": "探讨制度化对人性的磨损"},
            {"id": "a2", "title": "友谊作为抵抗", "description": "关系如何成为自由前提"},
            {"id": "a3", "title": "时间叙事", "description": "漫长岁月如何改变意义"},
        ]
    }
    svc = IdeationService(llm_client=llm)
    angles = svc.generate_angles(
        movie={"title": "肖申克的救赎", "year": 1994},
        opinions=[{"text": "hope", "source": "search"}],
    )
    assert len(angles) >= 3
    assert "剧情" not in angles[0]["title"]


def test_generate_two_distinct_routes():
    llm = MagicMock()
    llm.complete_json.side_effect = [
        {
            "routes": [
                {
                    "id": "r1",
                    "title": "哲学路线",
                    "outline": ["存在困境", "体制隐喻", "希望伦理"],
                },
                {
                    "id": "r2",
                    "title": "社会批判路线",
                    "outline": ["监狱权力结构", "制度化暴力", "个体觉醒"],
                },
            ]
        }
    ]
    svc = IdeationService(llm_client=llm)
    routes = svc.generate_routes(
        movie={"title": "肖申克的救赎"},
        angle={"id": "a1", "title": "体制与希望"},
        opinions=[{"text": "hope", "source": "search"}],
    )
    assert len(routes) == 2
    assert routes[0]["outline"] != routes[1]["outline"]


def test_select_angle_and_route_updates_session(db_session, researched_session):
    llm = MagicMock()
    llm.complete_json.return_value = {
        "routes": [
            {"id": "r1", "title": "路线A", "outline": ["论点1", "论点2"]},
            {"id": "r2", "title": "路线B", "outline": ["视角1", "视角2"]},
        ]
    }
    svc = IdeationService(llm_client=llm)

    angle = {"id": "a1", "title": "体制与希望", "description": "主题向"}
    svc.select_angle(db_session, researched_session.id, angle)
    db_session.refresh(researched_session)
    assert researched_session.selected_angle["id"] == "a1"

    routes = svc.generate_routes_for_session(db_session, researched_session.id)
    assert len(routes) == 2

    svc.select_route(db_session, researched_session.id, routes[1])
    db_session.refresh(researched_session)
    assert researched_session.selected_route["id"] == "r2"
    assert researched_session.status == SessionStatus.ROUTE_READY.value
