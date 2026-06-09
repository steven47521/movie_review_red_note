import json
from pathlib import Path
from unittest.mock import MagicMock

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
from app.services.ideation_service import IdeationService
from app.services.library_service import LibraryService
from app.services.persona_matcher import PersonaMatcher
from app.services.research_service import ResearchService
from app.llm.prompts.ideation import ANGLES_SYSTEM, ROUTES_SYSTEM
from app.llm.prompts.image_reviewer import IMAGE_MODERATOR_SYSTEM, IMAGE_REVIEWER_SYSTEM
from app.llm.prompts.moderator import MODERATOR_SYSTEM
from app.llm.prompts.reviewer import REVIEWER_SYSTEM
from app.llm.prompts.writer import DRAFT_SYSTEM, REVISION_SYSTEM
from app.services.review_orchestrator import ReviewOrchestrator
from app.services.visual_service import VisualService

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _persona_loader(ids):
    return [
        {
            "id": pid,
            "nickname": f"审稿人{pid[:4]}",
            "mbti": "INFJ",
            "age_band": "30s",
            "avatar_url": "/avatar.png",
        }
        for pid in ids
    ]


def _shared_llm():
    """LLM responses for ideation → draft → one text review round."""
    llm = MagicMock()
    reviewer_responses = [
        {"content": "思想深度不错。", "scores": {"depth": 8}},
        {"content": "角度新颖。", "scores": {"novelty": 7}},
        {"content": "可更口语化。", "scores": {"anti_ai": 7}},
    ]
    reviewer_calls = 0

    def complete_json(system, user, **kwargs):
        nonlocal reviewer_calls
        if system == ANGLES_SYSTEM:
            return {
                "angles": [
                    {"id": "a1", "title": "体制与希望", "description": "制度化主题"},
                    {"id": "a2", "title": "友谊与抵抗", "description": "关系伦理"},
                    {"id": "a3", "title": "时间叙事", "description": "意义变迁"},
                ]
            }
        if system == ROUTES_SYSTEM:
            return {
                "routes": [
                    {"id": "r1", "title": "情绪共鸣路线", "outline": ["开场", "共鸣", "收束"]},
                    {"id": "r2", "title": "结构拆解路线", "outline": ["镜头", "叙事", "主题"]},
                ]
            }
        if system == DRAFT_SYSTEM:
            return {
                "title": "肖申克的救赎：希望如何穿过高墙",
                "hooks": ["有些鸟注定不会被关住", "希望是好事，也许是人间至善"],
                "body": "从体制化视角讨论自由，而非剧情复述。",
                "tags": ["#肖申克", "#体制隐喻", "#希望哲学", "#影史经典", "#深度影评"],
            }
        if system == REVIEWER_SYSTEM:
            response = reviewer_responses[reviewer_calls % len(reviewer_responses)]
            reviewer_calls += 1
            return response
        if system == MODERATOR_SYSTEM:
            return {
                "content": "综合：加强标题吸引力。",
                "revision_instructions": "标题更悬念",
            }
        if system == REVISION_SYSTEM:
            return {
                "title": "关住的是身体，关不住的是希望",
                "hooks": ["监狱不是墙，是习惯", "希望是危险的，也是必要的"],
                "body": "修订后：从体制化视角谈自由伦理，避免套话。",
                "tags": ["#肖申克的救赎", "#自由意志", "#体制化", "#电影哲学", "#深夜影评"],
                "summary": "已按 moderator 意见修订。",
            }
        if system == IMAGE_REVIEWER_SYSTEM:
            return {"content": "配图整体不错。", "scores": {"style": 8}}
        if system == IMAGE_MODERATOR_SYSTEM:
            return {"content": "无需重生成。", "regenerate_types": []}
        raise AssertionError(f"unexpected system prompt: {system[:40]}")

    llm.complete_json.side_effect = complete_json
    return llm


def _mock_research_clients():
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
    return tmdb, search


def test_full_creation_flow_end_to_end(db_session):
    """Mock LLM/Image clients and walk the full creation state machine."""
    creation = CreationSession(movie_title="肖申克的救赎")
    db_session.add(creation)
    db_session.commit()
    session_id = creation.id

    tmdb, search = _mock_research_clients()
    research_svc = ResearchService(tmdb_client=tmdb, search_client=search)
    research = research_svc.research_and_persist(db_session, session_id, "肖申克的救赎")

    assert research["movie"]["year"] == 1994
    assert len(research["opinions"]) >= 3
    db_session.refresh(creation)
    assert creation.status == SessionStatus.ANGLES_READY.value

    llm = _shared_llm()
    ideation = IdeationService(llm_client=llm)
    angles = ideation.generate_angles_for_session(db_session, session_id)
    assert len(angles) >= 3
    ideation.select_angle(db_session, session_id, angles[0])

    routes = ideation.generate_routes_for_session(db_session, session_id)
    assert len(routes) == 2
    assert routes[0]["outline"] != routes[1]["outline"]
    ideation.select_route(db_session, session_id, routes[0])
    db_session.refresh(creation)
    assert creation.status == SessionStatus.ROUTE_READY.value

    matcher = PersonaMatcher()
    meta = db_session.query(MovieMeta).filter_by(session_id=session_id).one()
    panel = matcher.match_panel(
        {"title": meta.title, "genres": meta.genres or []},
        angle=angles[0],
    )
    assert 3 <= len(panel) <= 5
    creation.reviewer_panel_ids = [p["id"] for p in panel[:3]]
    db_session.commit()

    orch = ReviewOrchestrator(llm_client=llm, persona_loader=_persona_loader)
    draft = orch.generate_initial_draft(db_session, session_id)
    assert draft.title
    assert len(draft.hooks) >= 2
    assert len(draft.tags) >= 5

    orch.run_text_review_round(db_session, session_id)
    messages = (
        db_session.query(ReviewMessage)
        .filter_by(session_id=session_id, phase="text")
        .all()
    )
    roles = {m.role for m in messages}
    assert "reviewer" in roles
    assert "moderator" in roles
    assert "writer" in roles
    assert len([m for m in messages if m.role == "reviewer"]) >= 3

    orch.finalize_text(db_session, session_id)
    db_session.refresh(creation)
    assert creation.status == SessionStatus.TEXT_FINALIZED.value

    image_client = MagicMock()
    image_client.generate.side_effect = (
        lambda **kw: f"https://cdn.example/{kw['image_type']}.png"
    )
    visual = VisualService(db=db_session, image_client=image_client)
    images = visual.generate_all(session_id)
    assert len(images) >= 3
    assert {img.type for img in images} >= {"cover", "quote_card", "mood_shot"}

    orch.finalize(db_session, session_id)
    db_session.refresh(creation)
    assert creation.status == SessionStatus.COMPLETED.value

    library = LibraryService(db=db_session)
    timeline = library.get_timeline(session_id)
    event_types = {event["type"] for event in timeline}
    assert "research" in event_types
    assert "review_message" in event_types
    assert "draft_version" in event_types
    assert "image_asset" in event_types

    listed = library.list_sessions()
    assert any(s.id == session_id for s in listed)


def test_ac5_watery_draft_fixture_triggers_revision(db_session):
    """AC5: loaded watery draft should be revised after text review."""
    watery = json.loads((FIXTURES / "watery_draft.json").read_text(encoding="utf-8"))

    creation = CreationSession(
        movie_title="肖申克的救赎",
        status=SessionStatus.ROUTE_READY.value,
        selected_angle={"id": "a1", "title": "体制与希望", "description": "主题"},
        selected_route={"id": "r1", "title": "哲学路线", "outline": ["体制", "希望"]},
        reviewer_panel_ids=["p1", "p2", "p3"],
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
        ResearchSnapshot(
            session_id=creation.id,
            opinions=[{"text": "hope", "source": "search"}] * 3,
            sources_summary="search",
        )
    )
    db_session.commit()

    llm = MagicMock()
    reviewer_responses = [
        {"content": "AI感太重，缺乏具体论点。", "scores": {"anti_ai": 3}},
        {"content": "标题太模板。", "scores": {"title": 4}},
        {"content": "标签太泛。", "scores": {"tags": 3}},
    ]
    reviewer_calls = 0

    def complete_json(system, user, **kwargs):
        nonlocal reviewer_calls
        if system == DRAFT_SYSTEM:
            return watery
        if system == REVIEWER_SYSTEM:
            response = reviewer_responses[reviewer_calls % len(reviewer_responses)]
            reviewer_calls += 1
            return response
        if system == MODERATOR_SYSTEM:
            return {
                "content": "必须重写：去除综上所述，加入具体论点。",
                "revision_instructions": "去套话，加强观点句",
            }
        if system == REVISION_SYSTEM:
            return {
                "title": "当习惯成为牢笼",
                "hooks": ["自由不是出口，是选择"],
                "body": "从制度化视角看，主角的反抗是认知层面的越狱。",
                "tags": ["#体制隐喻", "#自由讨论", "#肖申克", "#电影笔记", "#思想影评"],
                "summary": "已去除 AI 套话并加强论点。",
            }
        raise AssertionError(f"unexpected system prompt: {system[:40]}")

    llm.complete_json.side_effect = complete_json

    orch = ReviewOrchestrator(llm_client=llm, persona_loader=_persona_loader)
    draft = orch.generate_initial_draft(db_session, creation.id)
    assert "综上所述" in draft.body

    orch.run_text_review_round(db_session, creation.id)
    latest = (
        db_session.query(DraftVersion)
        .filter_by(session_id=creation.id)
        .order_by(DraftVersion.version.desc())
        .first()
    )
    assert latest is not None
    assert "综上所述" not in latest.body

    reviewer_msgs = [
        m
        for m in db_session.query(ReviewMessage).filter_by(
            session_id=creation.id, phase="text", role="reviewer"
        )
    ]
    assert any("AI" in m.content or "套" in m.content for m in reviewer_msgs)


def test_persistence_survives_session_reload(db_session):
    """AC9: entities remain queryable after simulating a new DB session."""
    creation = CreationSession(movie_title="花样年华", status=SessionStatus.COMPLETED.value)
    db_session.add(creation)
    db_session.commit()
    session_id = creation.id

    db_session.add(
        ResearchSnapshot(
            session_id=session_id,
            opinions=[{"text": "loneliness", "source": "search"}] * 3,
            sources_summary="search",
        )
    )
    db_session.add(
        DraftVersion(
            session_id=session_id,
            version=1,
            title="标题",
            hooks=["h1", "h2"],
            body="正文",
            tags=["#t1", "#t2", "#t3", "#t4", "#t5"],
            review_round=1,
        )
    )
    db_session.add(
        ImageAsset(
            session_id=session_id,
            type="cover",
            url="https://cdn.example/cover.png",
            prompt="p",
            style_key="drama_film",
            version=1,
            review_round=1,
        )
    )
    db_session.add(
        ReviewMessage(
            session_id=session_id,
            phase="text",
            round=1,
            role="reviewer",
            content="不错的稿子",
        )
    )
    db_session.commit()

    engine = db_session.get_bind()
    with Session(engine) as fresh:
        assert fresh.query(ResearchSnapshot).filter_by(session_id=session_id).count() == 1
        assert fresh.query(DraftVersion).filter_by(session_id=session_id).count() == 1
        assert fresh.query(ImageAsset).filter_by(session_id=session_id).count() == 1
        assert fresh.query(ReviewMessage).filter_by(session_id=session_id).count() == 1
