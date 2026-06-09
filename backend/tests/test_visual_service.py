from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.session import Base
from app.models.creation_session import CreationSession, SessionStatus
from app.models.draft_version import DraftVersion
from app.models.image_asset import ImageAsset
from app.models.movie_meta import MovieMeta
from app.services.visual_service import VisualService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def visual_session(db_session):
    creation = CreationSession(
        movie_title="肖申克的救赎",
        status=SessionStatus.TEXT_FINALIZED.value,
        selected_angle={"id": "a1", "title": "体制与希望", "description": "主题"},
    )
    db_session.add(creation)
    db_session.commit()

    db_session.add(
        MovieMeta(
            session_id=creation.id,
            title="The Shawshank Redemption",
            year=1994,
            genres=["Drama", "Crime"],
        )
    )
    db_session.add(
        DraftVersion(
            session_id=creation.id,
            version=1,
            title="当习惯成为牢笼",
            hooks=["希望是好事"],
            body="从制度化视角看，自由是认知层面的越狱。",
            tags=["#肖申克", "#自由", "#电影哲学", "#深度影评", "#思想"],
            review_round=1,
        )
    )
    db_session.commit()
    return creation


def test_generate_images_returns_cover_and_content(db_session, visual_session):
    image_client = MagicMock()
    image_client.generate.side_effect = (
        lambda **kw: f"https://cdn.example/{kw['image_type']}.png"
    )
    svc = VisualService(db=db_session, image_client=image_client)

    assets = svc.generate_all(visual_session.id)

    types = {a.type for a in assets}
    assert "cover" in types
    assert "quote_card" in types
    assert "mood_shot" in types
    assert len(assets) >= 3
    assert image_client.generate.call_count >= 3


def test_regenerate_single_image(db_session, visual_session):
    image_client = MagicMock()
    image_client.generate.side_effect = [
        "https://cdn.example/cover_v1.png",
        "https://cdn.example/quote_card_v1.png",
        "https://cdn.example/mood_shot_v1.png",
        "https://cdn.example/cover_v2.png",
    ]
    svc = VisualService(db=db_session, image_client=image_client)
    assets = svc.generate_all(visual_session.id)
    cover = next(a for a in assets if a.type == "cover")

    new_asset = svc.regenerate_image(cover.id, reason="封面不够吸引")
    assert new_asset.version == cover.version + 1
    assert new_asset.url != cover.url
