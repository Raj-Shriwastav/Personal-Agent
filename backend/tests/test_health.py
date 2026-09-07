import pytest
from fastapi.testclient import TestClient

from app.db.session import check_database_connection


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app"] == "Personal AI Agent"


def test_db_health_always_answers_with_valid_schema(client: TestClient) -> None:
    """Whatever the DB state, the endpoint must answer, never crash."""
    response = client.get("/api/health/db")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in {"ok", "error"}
    assert body["database"] in {"connected", "unreachable"}


def test_db_health_is_connected_when_postgres_is_running(client: TestClient) -> None:
    """The real Phase 1 check. Only meaningful with PostgreSQL up."""
    if not check_database_connection():
        pytest.skip("PostgreSQL is not reachable; start it with `docker compose up -d db`")
    body = client.get("/api/health/db").json()
    assert body == {
        "status": "ok",
        "database": "connected",
        "detail": "SELECT 1 succeeded",
    }
