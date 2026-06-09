from unittest.mock import MagicMock, patch

from tests.test_research_api import client


@patch("app.api.routes.sessions.IdeationService")
def test_generate_angles_api(mock_service_cls):
    mock_svc = MagicMock()
    mock_svc.generate_angles_for_session.return_value = [
        {"id": "a1", "title": "体制与希望", "description": "主题向"},
        {"id": "a2", "title": "友谊与自由", "description": "关系向"},
        {"id": "a3", "title": "时间与人性", "description": "叙事向"},
    ]
    mock_service_cls.return_value = mock_svc

    create_resp = client.post(
        "/api/v1/sessions", json={"title": "肖申克的救赎", "year": 1994}
    )
    session_id = create_resp.json()["id"]

    resp = client.post(f"/api/v1/sessions/{session_id}/angles/generate")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 3
    assert "剧情" not in data["angles"][0]["title"]
