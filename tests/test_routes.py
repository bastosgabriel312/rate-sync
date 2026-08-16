# tests/test_routes.py

from fastapi.testclient import TestClient

from app.main import app


def test_health():
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "timestamp" in body
    assert "version" in body


def test_ratings_returns_three_sources():
    client = TestClient(app)
    response = client.get("/api/v1/ratings/Inception")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"cinemeta", "omdb", "letterboxd"}
    assert "rating" in body["cinemeta"] or "error" in body["cinemeta"]