from unittest.mock import MagicMock, patch

from tests.test_research_api import client


@patch("app.api.routes.review.DraftService")
def test_regenerate_title_api(mock_svc_cls):
    mock_draft = MagicMock()
    mock_draft.version = 2
    mock_draft.title = "新标题"
    mock_draft.hooks = ["h1"]
    mock_draft.body = "正文不变"
    mock_draft.tags = ["#tag"]
    mock_svc = MagicMock()
    mock_svc.regenerate_part.return_value = mock_draft
    mock_svc_cls.return_value = mock_svc

    create = client.post("/api/v1/sessions", json={"title": "肖申克的救赎"})
    session_id = create.json()["id"]

    resp = client.post(
        f"/api/v1/sessions/{session_id}/draft/regenerate",
        json={"part": "title"},
    )
    assert resp.status_code == 200
    assert resp.json()["part"] == "title"
    assert resp.json()["draft"]["title"] == "新标题"
