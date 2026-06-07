"""Tests for the /health endpoint."""
from typing import Any

from fastapi.testclient import TestClient

from app.config import Settings
from app.connectors.sheets import SheetsRepository
from app.main import create_app


def _client_without_sheets() -> TestClient:
    app = create_app()
    app.state.sheets_repository = None
    return TestClient(app)


def _fake_repository(healthy: bool = True) -> SheetsRepository:
    class _FakeClient:
        def __init__(self, healthy: bool) -> None:
            self._healthy = healthy

        def read_records(self, _: str) -> list[dict[str, Any]]:
            return []

        def health_check(self) -> bool:
            return self._healthy

    return SheetsRepository(client=_FakeClient(healthy), settings=Settings())


def _client_with_repository(healthy: bool) -> TestClient:
    app = create_app()
    app.state.sheets_repository = _fake_repository(healthy)
    return TestClient(app)


# ------------------------------------------------------------------ baseline


def test_health_endpoint_returns_ok() -> None:
    client = _client_without_sheets()

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_includes_environment() -> None:
    client = _client_without_sheets()

    body = client.get("/api/v1/health").json()

    assert body["environment"] == "local"


# ------------------------------------------ sheets_configured / sheets_healthy


def test_health_sheets_configured_false_without_credentials() -> None:
    client = _client_without_sheets()

    body = client.get("/api/v1/health").json()

    assert body["sheets_configured"] is False
    assert body["sheets_healthy"] is None


def test_health_sheets_healthy_true_when_repository_reports_healthy() -> None:
    client = _client_with_repository(healthy=True)

    body = client.get("/api/v1/health").json()

    assert body["sheets_healthy"] is True


def test_health_sheets_healthy_false_when_repository_reports_unhealthy() -> None:
    client = _client_with_repository(healthy=False)

    body = client.get("/api/v1/health").json()

    assert body["sheets_healthy"] is False
