import threading
import time
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.session import Base
from app.models.creation_session import CreationSession, SessionStatus
from app.models.draft_version import DraftVersion
from app.models.movie_meta import MovieMeta
from app.models.research_snapshot import ResearchSnapshot
from app.models.review_message import ReviewMessage
from app.llm.prompts.moderator import MODERATOR_SYSTEM
from app.llm.prompts.reviewer import REVIEWER_SYSTEM
from app.llm.prompts.writer import DRAFT_SYSTEM, REVISION_SYSTEM
from app.services.review_orchestrator import ReviewOrchestrator, ReviewRoundLimitError


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def route_ready_session(db_session):
    creation = CreationSession(
        movie_title="肖申克的救赎",
        status=SessionStatus.ROUTE_READY.value,
        selected_angle={"id": "a1", "title": "体制与希望", "description": "主题向"},
        selected_route={
            "id": "r1",
            "title": "哲学路线",
            "outline": ["体制", "希望", "自由"],
        },
        reviewer_panel_ids=["p1", "p2", "p3"],
        text_review_round=0,
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
    return creation


def _mock_llm():
    llm = MagicMock()
    reviewer_responses = [
        {"content": "思想深度不错，但标题还能更抓人。", "scores": {"depth": 8}},
        {"content": "角度新颖，略缺小红书网感。", "scores": {"novelty": 7}},
        {"content": "反AI感尚可，可再口语化。", "scores": {"anti_ai": 7}},
    ]
    reviewer_calls = 0

    def complete_json(system, user):
        nonlocal reviewer_calls
        if system == DRAFT_SYSTEM:
            return {
                "title": "体制里开出的花",
                "hooks": ["有些鸟注定不会被关住", "希望是好事，也许是人间至善"],
                "body": "这篇影评讨论体制与希望，而非剧情复述。",
                "tags": ["#肖申克", "#体制隐喻", "#希望哲学", "#影史经典", "#深度影评"],
            }
        if system == REVIEWER_SYSTEM:
            response = reviewer_responses[reviewer_calls % len(reviewer_responses)]
            reviewer_calls += 1
            return response
        if system == MODERATOR_SYSTEM:
            return {
                "content": "综合：加强标题吸引力与标签网感。",
                "revision_instructions": "标题更悬念；标签更话题化",
            }
        if system == REVISION_SYSTEM:
            return {
                "title": "关住的是身体，关不住的是希望",
                "hooks": ["监狱不是墙，是习惯", "希望是危险的，也是必要的"],
                "body": "修订后正文：从体制化视角谈自由伦理，避免套话。",
                "tags": ["#肖申克的救赎", "#自由意志", "#体制化", "#电影哲学", "#深夜影评"],
                "summary": "已按 moderator 意见修订标题与标签。",
            }
        raise AssertionError(f"unexpected system prompt: {system[:40]}")

    llm.complete_json.side_effect = complete_json
    llm.complete_text.return_value = "fallback text"
    return llm


def test_text_review_round_persists_messages(db_session, route_ready_session):
    llm = _mock_llm()
    orch = ReviewOrchestrator(llm_client=llm, persona_loader=lambda ids: [
        {"id": i, "nickname": f"审稿人{i}", "mbti": "INFJ", "age_band": "30s", "avatar_url": "/a.png"}
        for i in ids
    ])
    orch.generate_initial_draft(db_session, route_ready_session.id)
    orch.run_text_review_round(db_session, route_ready_session.id)

    messages = (
        db_session.query(ReviewMessage)
        .filter_by(session_id=route_ready_session.id, phase="text")
        .all()
    )
    roles = {m.role for m in messages}
    assert "reviewer" in roles
    assert "moderator" in roles
    assert "writer" in roles
    assert len([m for m in messages if m.role == "reviewer"]) >= 3


def test_text_review_round_runs_reviewers_in_parallel(db_session, route_ready_session):
    llm = MagicMock()
    active = 0
    max_active = 0
    lock = threading.Lock()
    gate = threading.Barrier(3)

    def complete_json(system, user):
        nonlocal active, max_active
        if system == DRAFT_SYSTEM:
            return {
                "title": "标题",
                "hooks": ["hook1", "hook2"],
                "body": "正文",
                "tags": ["#a", "#b", "#c", "#d", "#e"],
            }
        if system == REVIEWER_SYSTEM:
            with lock:
                active += 1
                max_active = max(max_active, active)
            gate.wait(timeout=2)
            time.sleep(0.05)
            with lock:
                active -= 1
            return {"content": "并行审稿", "scores": {"depth": 8}}
        if system == MODERATOR_SYSTEM:
            return {"content": "汇总", "revision_instructions": "优化标题"}
        if system == REVISION_SYSTEM:
            return {
                "title": "新标题",
                "hooks": ["hook1", "hook2"],
                "body": "新正文",
                "tags": ["#a", "#b", "#c", "#d", "#e"],
                "summary": "已修订",
            }
        raise AssertionError(f"unexpected system prompt: {system[:40]}")

    llm.complete_json.side_effect = complete_json
    orch = ReviewOrchestrator(
        llm_client=llm,
        persona_loader=lambda ids: [
            {"id": i, "nickname": f"审稿人{i}", "mbti": "INFJ", "age_band": "30s", "avatar_url": "/a.png"}
            for i in ids
        ],
    )
    orch.generate_initial_draft(db_session, route_ready_session.id)
    orch.run_text_review_round(db_session, route_ready_session.id)
    assert max_active >= 2


def test_text_review_round_limit_five():
    orch = ReviewOrchestrator(max_rounds=5)
    with pytest.raises(ReviewRoundLimitError):
        orch.ensure_can_continue(text_review_round=5)


def test_watery_draft_gets_revision(db_session, route_ready_session):
    llm = MagicMock()
    reviewer_responses = [
        {"content": "AI感太重，缺乏具体论点。", "scores": {"anti_ai": 3}},
        {"content": "标题太模板。", "scores": {"title": 4}},
        {"content": "标签太泛。", "scores": {"tags": 3}},
    ]
    reviewer_calls = 0

    def complete_json(system, user):
        nonlocal reviewer_calls
        if system == DRAFT_SYSTEM:
            return {
                "title": "这部电影很好看",
                "hooks": ["综上所述值得一看"],
                "body": "综上所述，这部电影深刻地揭示了人性的复杂，非常好看。",
                "tags": ["#经典电影", "#深度影评"],
            }
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
    orch = ReviewOrchestrator(
        llm_client=llm,
        persona_loader=lambda ids: [
            {"id": i, "nickname": f"R{i}", "mbti": "INTJ", "age_band": "40s", "avatar_url": "/a.png"}
            for i in ids
        ],
    )
    draft = orch.generate_initial_draft(db_session, route_ready_session.id)
    assert "综上所述" in draft.body

    orch.run_text_review_round(db_session, route_ready_session.id)
    latest = (
        db_session.query(DraftVersion)
        .filter_by(session_id=route_ready_session.id)
        .order_by(DraftVersion.version.desc())
        .first()
    )
    assert "综上所述" not in latest.body
