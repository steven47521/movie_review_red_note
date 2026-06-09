from unittest.mock import MagicMock, patch

from tests.test_research_api import client


@patch("app.api.routes.review.ReviewOrchestrator")
def test_finalize_text_api(mock_orch_cls):
    mock_orch = MagicMock()
    mock_session = MagicMock()
    mock_session.status = "text_finalized"
    mock_orch.finalize_text.return_value = mock_session
    mock_orch_cls.return_value = mock_orch

    create = client.post("/api/v1/sessions", json={"title": "肖申克的救赎"})
    session_id = create.json()["id"]

    resp = client.post(f"/api/v1/sessions/{session_id}/review/finalize-text")
    assert resp.status_code == 200
    assert resp.json()["status"] == "text_finalized"
