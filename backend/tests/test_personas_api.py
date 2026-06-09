from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_personas_returns_80():
    response = client.get("/api/v1/personas")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 80
    assert len(data["personas"]) == 80
